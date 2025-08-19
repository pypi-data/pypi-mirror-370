# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import functools
import hashlib
import json
import logging
import uuid
from collections import Counter
from collections.abc import Generator, Iterator
from typing import Any, cast

import attrs
import cloudpickle
import lance
import pyarrow as pa
import ray.actor
import ray.exceptions
import ray.util.queue
from ray.actor import ActorHandle
from tqdm.std import tqdm as TqdmType  # noqa: N812

from geneva.apply import (
    CheckpointingApplier,
    plan_copy,
    plan_read,
)
from geneva.apply.applier import BatchApplier
from geneva.apply.multiprocess import MultiProcessBatchApplier
from geneva.apply.simple import SimpleApplier
from geneva.apply.task import BackfillUDFTask, CopyTableTask, MapTask, ReadTask
from geneva.checkpoint import CheckpointStore
from geneva.debug.logger import CheckpointStoreErrorLogger
from geneva.job.config import JobConfig
from geneva.packager import UDFPackager
from geneva.query import (
    MATVIEW_META_BASE_DBURI,
    MATVIEW_META_BASE_TABLE,
    MATVIEW_META_BASE_VERSION,
    MATVIEW_META_QUERY,
    GenevaQuery,
    GenevaQueryBuilder,
)
from geneva.runners.ray.actor_pool import ActorPool
from geneva.runners.ray.jobtracker import JobTracker
from geneva.runners.ray.raycluster import CPU_ONLY_NODE, ray_tqdm
from geneva.runners.ray.writer import FragmentWriter
from geneva.table import JobFuture, Table, TableReference
from geneva.tqdm import tqdm
from geneva.transformer import UDF

_LOG = logging.getLogger(__name__)


@ray.remote
@attrs.define
class ApplierActor:
    applier: CheckpointingApplier

    def __ray_ready__(self) -> None:
        pass

    def run(self, task) -> tuple[ReadTask, str]:
        return task, self.applier.run(task)


ApplierActor: ray.actor.ActorClass = cast("ray.actor.ActorClass", ApplierActor)


def _get_fragment_dedupe_key(uri: str, frag_id: int, map_task: MapTask) -> str:
    key = f"{uri}:{frag_id}:{map_task.checkpoint_key()}"
    return hashlib.sha256(key.encode()).hexdigest()


def _run_column_adding_pipeline(
    map_task: MapTask,
    checkpoint_store: CheckpointStore,
    config: JobConfig,
    dst: TableReference,
    input_plan: Iterator[ReadTask],
    job_id: str | None,
    applier_concurrency: int = 8,
    *,
    intra_applier_concurrency: int = 1,
    use_cpu_only_pool: bool = False,
    job_tracker=None,
    where=None,
) -> None:
    """
    Run the column adding pipeline.

    Args:
    * use_cpu_only_pool: If True will force schedule cpu-only actors on cpu-only nodes.

    """
    job_id = job_id or uuid.uuid4().hex
    job_tracker = job_tracker or JobTracker.options(
        name=f"jobtracker-{job_id}",
        num_cpus=0.1,
        memory=128 * 1024 * 1024,
        max_restarts=-1,
    ).remote(job_id)
    job = ColumnAddPipelineJob(
        map_task=map_task,
        checkpoint_store=checkpoint_store,
        config=config,
        dst=dst,
        input_plan=input_plan,
        job_id=job_id,
        applier_concurrency=applier_concurrency,
        intra_applier_concurrency=intra_applier_concurrency,
        use_cpu_only_pool=use_cpu_only_pool,
        job_tracker=job_tracker,
        where=where,
    )
    job.run()


@attrs.define
class ColumnAddPipelineJob:
    """ColumnAddPipeline drives batches of rows to commits in the dataset.

    ReadTasks are defined wrapped for tracking, and then dispatched for udf exeuction
    in the ActorPool.  The results are sent to the FragmentWriterManager which
    manages fragment checkpoints and incremental commits.
    """

    map_task: MapTask
    checkpoint_store: CheckpointStore
    config: JobConfig
    dst: TableReference
    input_plan: Iterator[ReadTask]
    job_id: str
    applier_concurrency: int = 8
    intra_applier_concurrency: int = 1
    use_cpu_only_pool: bool = False
    job_tracker: ActorHandle | None = None
    where: str | None = None
    _total_rows: int = attrs.field(default=0, init=False)

    def setup_inputplans(self) -> (Iterator[ReadTask], int):
        all_tasks = list(self.input_plan)
        self.job_tracker = self.job_tracker or JobTracker.options(
            name=f"jobtracker-{self.job_id}",
            num_cpus=0.1,
            memory=128 * 1024 * 1024,
            max_restarts=-1,
        ).remote(self.job_id)

        self._total_rows = sum(t.num_rows() for t in all_tasks)
        plan_len = len(all_tasks)

        # fragments
        self.job_tracker.set_total.remote("fragments", plan_len)
        self.job_tracker.set_desc.remote(
            "fragments",
            f"[{self.dst.table_name} - {self.map_task.name()}] Batches scheduled",
        )

        # this reports # of batches started, not completed.
        tasks_by_frag = Counter(t.dest_frag_id() for t in all_tasks)
        return (
            ray_tqdm(all_tasks, self.job_tracker, metric="fragments"),
            tasks_by_frag,
            plan_len,
        )

    def setup_actor(self) -> None:
        actor = ApplierActor

        # actor.options can only be called once, we must pass all override args
        # in one shot
        args = {
            "num_cpus": self.map_task.num_cpus() * self.intra_applier_concurrency,
        }
        if self.map_task.is_cuda():
            args["num_gpus"] = 1
        elif self.use_cpu_only_pool:
            _LOG.info("Using CPU only pool for applier, setting %s to 1", CPU_ONLY_NODE)
            args["resources"] = {CPU_ONLY_NODE: 1}
        if self.map_task.memory():
            args["memory"] = self.map_task.memory() * self.intra_applier_concurrency
        actor = actor.options(**args)
        return actor

    def setup_batchapplier(self) -> BatchApplier:
        if self.intra_applier_concurrency > 1:
            return MultiProcessBatchApplier(
                num_processes=self.intra_applier_concurrency
            )
        else:
            return SimpleApplier()

    def setup_actorpool(self) -> ActorPool:
        batch_applier = self.setup_batchapplier()

        applier = CheckpointingApplier(
            map_task=self.map_task,
            batch_applier=batch_applier,
            checkpoint_store=self.checkpoint_store,
            error_logger=CheckpointStoreErrorLogger(self.job_id, self.checkpoint_store),
        )

        actor = self.setup_actor()
        self.job_tracker.set_total.remote("workers", self.applier_concurrency)
        self.job_tracker.set_desc.remote("workers", "Workers started")

        pool = ActorPool(
            functools.partial(actor.remote, applier=applier),
            self.applier_concurrency,
            job_tracker=self.job_tracker,
            worker_metric="workers",
        )
        return pool

    def setup_writertracker(self) -> (lance.LanceDataset, int):
        ds = self.dst.open().to_lance()
        fragments = ds.get_fragments()
        len_frags = len(fragments)

        self.job_tracker.set_total.remote("writer_fragments", len_frags)
        self.job_tracker.set_desc.remote("writer_fragments", "Fragments written")
        ray_tqdm(fragments, self.job_tracker, metric="writer_fragments")

        return ds, len_frags

    def run(self) -> None:
        plans, tasks_by_frag, cnt_batches = self.setup_inputplans()
        pool = self.setup_actorpool()
        ds, cnt_fragments = self.setup_writertracker()

        prefix = f"[{self.dst.table_name} - {self.map_task.name()}]"
        # rows metrics (all cumulative)
        for m, desc in [
            (
                "rows_checkpointed",
                f"{prefix} Rows checkpointed",
            ),
            (
                "rows_ready_for_commit",
                f"{prefix} Rows ready for commit",
            ),
            (
                "rows_committed",
                f"{prefix} Rows committed",
            ),
        ]:
            self.job_tracker.set_total.remote(m, self._total_rows)
            self.job_tracker.set_desc.remote(m, desc)

        _LOG.info(
            f"Pipeline executing on {cnt_batches} batches over "
            f"{cnt_fragments} table fragments"
        )

        # kick off the applier actors
        applier_iter = pool.map_unordered(
            lambda actor, value: actor.run.remote(value),
            # the API says list, but iterables are fine
            plans,
        )

        fwm = FragmentWriterManager(
            ds.version,
            ds_uri=ds.uri,
            map_task=self.map_task,
            checkpoint_store=self.checkpoint_store,
            where=self.where,
            job_tracker=self.job_tracker,
            commit_granularity=self.config.commit_granularity,
            expected_tasks=dict(tasks_by_frag),
        )

        for task, result in applier_iter:
            fwm.ingest(result, task)
            # ensure we discover any frgments that finished writing even if the
            # current task belongs to another fragment.
            fwm.poll_all()

        pool.shutdown()
        fwm.cleanup()


@attrs.define
class FragmentWriterSession:
    """This tracks all the batch tasks for a single fragment.

    It is responsible for managing the fragment writer's life cycle and does the
    bookkeeping of inflight tasks, completed tasks, and the queue of tasks to write.
    These are locally tracked and accounted for before the fragment is considered
    complete and ready to be commited to the dataset.

    It expects to be initialized and then fed with `ingest_task` calls. After all tasks
    have been added, it is `seal`ed meaning no more input tasks are expected.  Then it
    can be `drain`ed to yield all completed tasks.
    """

    frag_id: int
    ds_uri: str
    output_columns: list[str]
    checkpoint_store: CheckpointStore
    where: str | None

    # runtime state.  This is single-threaded and is not thread-safe.
    queue: ray.util.queue.Queue = attrs.field(factory=ray.util.queue.Queue, init=False)
    actor: ActorHandle = attrs.field(init=False)
    cached_tasks: list[tuple[int, Any]] = attrs.field(factory=list, init=False)
    inflight: dict[ray.ObjectRef, int] = attrs.field(factory=dict, init=False)
    _shutdown: bool = attrs.field(default=False, init=False)

    sealed: bool = attrs.field(default=False, init=False)  # no more tasks will be added
    enqueued: int = attrs.field(default=0, init=False)  # total expected tasks
    completed: int = attrs.field(default=0, init=False)  # total compelted tasks

    def __attrs_post_init__(self) -> None:
        self._start_writer()

    def _start_writer(self) -> None:
        self.actor = FragmentWriter.options(
            num_cpus=0.1,  # make it cheap to schedule (not require full cpu)
            memory=1024 * 1024 * 1024,  # 1gb ram
        ).remote(
            self.ds_uri,
            self.output_columns,
            self.checkpoint_store,
            self.frag_id,
            self.queue,
            where=self.where,
        )
        # prime one future so we can detect when it finishes
        fut = self.actor.write.remote()
        self.inflight[fut] = self.frag_id

    def shutdown(self) -> None:
        len_inflight = len(self.inflight)
        if len_inflight > 0:
            try:
                is_empty = self.queue.empty()
            except (ray.exceptions.RayError, Exception):
                # queue actor died or unavailble.  assume empty
                is_empty = True
                # queue should be empty and inflight should be 0.
                _LOG.warning(
                    "Shutting down frag %s - queue empty %s, inflight: %d",
                    self.frag_id,
                    is_empty,
                    len_inflight,
                )

        if self._shutdown:
            return  # idempotent
        self.queue.shutdown()
        ray.kill(self.actor)
        self._shutdown = True

    def _restart(self) -> None:
        self.shutdown()

        # make it cheap to schedule (not require full cpu, reserve 256MiB ram)
        self.queue = ray.util.queue.Queue(
            actor_options={"num_cpus": 0.1, "memory": 256 * 1024 * 1024}
        )
        self.inflight.clear()
        self.cached_tasks, old_tasks = [], self.cached_tasks
        self.__attrs_post_init__()  # recreates writer & first future

        # replay tasks
        for off, res in old_tasks:
            self.queue.put((off, res))

    def ingest_task(self, offset: int, result: Any) -> None:
        """Called by manager when a new (offset, result) arrives."""
        self.cached_tasks.append((offset, result))
        self.enqueued += 1
        try:
            self.queue.put((offset, result))
        except (ray.exceptions.ActorDiedError, ray.exceptions.ActorUnavailableError):
            _LOG.warning("Writer actor for frag %s died – restarting", self.frag_id)
            self._restart()

    def poll_ready(self) -> list[tuple[int, Any, int]]:
        """Non‑blocking check for any finished futures.
        Returns list of (frag_id, new_file, rows_written) that completed."""
        ready, _ = ray.wait(list(self.inflight.keys()), timeout=0.0)
        completed: list[tuple[int, Any, int]] = []

        for fut in ready:
            try:
                res = ray.get(fut)
                assert isinstance(res, tuple) and len(res) == 3, (  # noqa: PT018
                    "FragmentWriter.write() should return (frag_id, new_file,"
                    " rows_written), "
                )
                fid, new_file, rows_written = res
                completed.append((fid, new_file, rows_written))
            except (
                ray.exceptions.ActorDiedError,
                ray.exceptions.ActorUnavailableError,
            ):
                _LOG.warning(
                    "Writer actor for frag %s unavailable – restarting", self.frag_id
                )
                self._restart()
                return []  # will show up next poll
            assert fid == self.frag_id
            self.completed += 1
            self.inflight.pop(fut)

        return completed

    def seal(self) -> None:
        self.sealed = True

    def drain(self) -> Generator[tuple[int, Any, int], None, None]:
        """Yield all (frag_id,new_file, rows_written) as futures complete."""
        while self.inflight:
            ready, _ = ray.wait(list(self.inflight.keys()), timeout=5.0)
            if not ready:
                continue

            for fut in ready:
                try:
                    res = ray.get(fut)
                    assert isinstance(res, tuple) and len(res) == 3, (  # noqa: PT018
                        "FragmentWriter.write() should return (frag_id, new_file,"
                        " rows_written), "
                    )
                    fid, new_file, rows_written = res
                    yield fid, new_file, rows_written
                    self.completed += 1
                except (
                    ray.exceptions.ActorDiedError,
                    ray.exceptions.ActorUnavailableError,
                ):
                    _LOG.warning(
                        "Writer actor for frag %s died during drain—restarting",
                        self.frag_id,
                    )
                    # clear out any old futures, spin up a fresh actor & queue
                    self._restart()
                    # break out to re-enter the while loop with a clean slate
                    break
                # sucessful write
                self.inflight.pop(fut)


@attrs.define
class FragmentWriterManager:
    """FragmentWriterManager is responsible for writing out fragments
    from the ReadTasks to the destination dataset.

    There is one instance so that we can track pending completed fragments and do
    partial commits.
    """

    dst_read_version: int
    ds_uri: str
    map_task: MapTask
    checkpoint_store: CheckpointStore
    where: str | None
    job_tracker: ActorHandle
    commit_granularity: int
    expected_tasks: dict[int, int]  # frag_id, # batches

    # internal state
    sessions: dict[int, FragmentWriterSession] = attrs.field(factory=dict, init=False)
    remaining_tasks: dict[int, int] = attrs.field(init=False)
    output_columns: list[str] = attrs.field(init=False)
    # (frag_id, lance.fragment.DataFile, # rows)
    rows_input_by_frag: dict[int, int] = attrs.field(factory=dict, init=False)
    to_commit: list[tuple[int, lance.fragment.DataFile, int]] = attrs.field(
        factory=list, init=False
    )

    def __attrs_post_init__(self) -> None:
        # all output cols except for _rowaddr because it is implicit since the
        # lancedatafile is writing out in sequential order
        self.output_columns = [
            f.name for f in self.map_task.output_schema() if f.name != "_rowaddr"
        ]
        self.remaining_tasks = dict(self.expected_tasks)

    def poll_all(self) -> None:
        for sess in list(self.sessions.values()):
            for fid, new_file, rows_written in sess.poll_ready():
                self._record_fragment(
                    fid, new_file, self.commit_granularity, rows_written
                )

    def ingest(self, result, task) -> None:
        frag_id = task.dest_frag_id()

        sess = self.sessions.get(frag_id)
        if sess is None:
            _LOG.debug("Creating writer for fragment %d", frag_id)
            sess = FragmentWriterSession(
                frag_id=frag_id,
                ds_uri=self.ds_uri,
                output_columns=self.output_columns,
                checkpoint_store=self.checkpoint_store,
                where=self.where,
            )
            self.sessions[frag_id] = sess

        sess.ingest_task(task.dest_offset(), result)
        try:
            num_rows = getattr(task, "num_rows", None)
            if callable(num_rows):
                num_rows = num_rows()
            if isinstance(num_rows, int) and num_rows > 0:
                self.job_tracker.increment.remote("rows_checkpointed", num_rows)
                self.rows_input_by_frag[frag_id] = self.rows_input_by_frag.get(
                    frag_id, 0
                ) + int(num_rows)
        except Exception:
            _LOG.exception("Failed to get number of rows from result for task %s", task)
        self.remaining_tasks[frag_id] -= 1
        if self.remaining_tasks[frag_id] <= 0:
            sess.seal()

        # TODO check if previously checkpointed fragment exists

    def _record_fragment(
        self,
        frag_id: int,
        new_file,
        commit_granularity: int,
        rows_written: int,
    ) -> None:
        dedupe_key = _get_fragment_dedupe_key(self.ds_uri, frag_id, self.map_task)
        # store file name in case of a failure or delete and recalc reuse.
        self.checkpoint_store[dedupe_key] = pa.RecordBatch.from_pydict(
            {"file": new_file.path}
        )
        self.job_tracker.increment.remote("writer_fragments", 1)

        input_rows = int(self.rows_input_by_frag.get(frag_id, 0))
        self.to_commit.append((frag_id, new_file, input_rows))
        if input_rows > 0:
            self.job_tracker.increment.remote("rows_ready_for_commit", input_rows)

        # Track processed writes and hybrid-shutdown
        sess = self.sessions.get(frag_id)
        if sess and sess.sealed and not sess.inflight:
            # flush any pending commit for this fragment
            sess.shutdown()
            self.sessions.pop(frag_id, None)

        self._commit_if_n_fragments(commit_granularity)

    # aka _try_commit
    def _commit_if_n_fragments(self, commit_granularity: int) -> None:
        n = max(1, int(commit_granularity))
        if len(self.to_commit) < n:
            return

        to_commit = self.to_commit
        self.to_commit = []
        version = self.dst_read_version
        self.dst_read_version += 1

        operation = lance.LanceOperation.DataReplacement(
            replacements=[
                lance.LanceOperation.DataReplacementGroup(
                    fragment_id=frag_id,
                    new_file=new_file,
                )
                for frag_id, new_file, _rows in to_commit
            ]
        )

        while True:
            try:
                _LOG.info(
                    "Committing %d fragments to %s at version %d",
                    len(to_commit),
                    self.ds_uri,
                    version,
                )
                lance.LanceDataset.commit(self.ds_uri, operation, read_version=version)
                # rows committed == sum(input rows for fragments just committed)
                committed_rows = sum((_rows for _fid, _new_file, _rows in to_commit))
                if committed_rows:
                    self.job_tracker.increment.remote("rows_committed", committed_rows)

                break
            except OSError as e:
                # Conflict error has this message:
                # OSError: Commit conflict for version 6: This DataReplacement \
                # transaction is incompatible with concurrent transaction \
                # DataReplacement at version 6.,
                if "Commit conflict for version" not in str(e):
                    # only handle version conflict
                    raise e

                # WARNING - the versions are sequentially increasing and we assume we'll
                # eventually find a version that will not conflict.  This could be a
                # problem for rare cases where column replacemnts happen concurrently.

                # TODO: This is a workaround for now, but we should consider adding
                # conflict resolution to lance.

                # this is a version conflict, retry with next version
                _LOG.warning(
                    "Commit failed with version conflict: %s. Retrying with next"
                    " version.",
                    e,
                )
                version += 1

    def cleanup(self) -> None:
        _LOG.debug("draining & shutting down any leftover sessions")

        # 1) Commit any top‑of‑buffer fragments
        self._commit_if_n_fragments(1)

        # 2) Drain & shutdown whatever sessions remain
        for _frag_id, sess in list(self.sessions.items()):
            for fid, new_file, rows_written in sess.drain():
                # this may in turn pop more sessions via _record_fragment
                self._record_fragment(
                    fid, new_file, self.commit_granularity, rows_written
                )
            sess.shutdown()

        # 3) Clear out any sessions that finished in the loop above
        self.sessions.clear()

        # 4) Final safety commit of anything left
        self._commit_if_n_fragments(1)


def run_ray_copy_table(
    dst: TableReference,
    packager: UDFPackager,
    checkpoint_store: CheckpointStore | None = None,
    *,
    job_id: str | None = None,
    concurrency: int = 8,
    batch_size: int | None = None,
    task_shuffle_diversity: int | None = None,
    commit_granularity: int | None = None,
    **kwargs,
) -> None:
    # prepare job parameters
    config = JobConfig.get().with_overrides(
        batch_size=batch_size,
        task_shuffle_diversity=task_shuffle_diversity,
        commit_granularity=commit_granularity,
    )

    checkpoint_store = checkpoint_store or config.make_checkpoint_store()

    dst_schema = dst.open().schema
    if dst_schema.metadata is None:
        raise Exception("Destination dataset must have view metadata.")
    src_dburi = dst_schema.metadata[MATVIEW_META_BASE_DBURI.encode("utf-8")].decode(
        "utf-8"
    )
    src_name = dst_schema.metadata[MATVIEW_META_BASE_TABLE.encode("utf-8")].decode(
        "utf-8"
    )
    src_version = int(
        dst_schema.metadata[MATVIEW_META_BASE_VERSION.encode("utf-8")].decode("utf-8")
    )
    src = TableReference(db_uri=src_dburi, table_name=src_name, version=src_version)
    query_json = dst_schema.metadata[MATVIEW_META_QUERY.encode("utf-8")]
    query = GenevaQuery.model_validate_json(query_json)

    src_table = src.open()
    schema = GenevaQueryBuilder.from_query_object(src_table, query).schema

    job_id = job_id or uuid.uuid4().hex

    column_udfs = query.extract_column_udfs(packager)

    # take all cols (excluding some internal columns) since contents are needed to feed
    # udfs or copy src table data
    input_cols = [
        n for n in src_table.schema.names if n not in ["__is_set", "__source_row_id"]
    ]

    plan = plan_copy(
        src,
        dst,
        input_cols,
        batch_size=config.batch_size,
        task_shuffle_diversity=config.task_shuffle_diversity,
    )

    map_task = CopyTableTask(
        column_udfs=column_udfs, view_name=dst.table_name, schema=schema
    )

    _run_column_adding_pipeline(
        map_task,
        checkpoint_store,
        config,
        dst,
        plan,
        job_id,
        concurrency,
        **kwargs,
    )


def dispatch_run_ray_add_column(
    table_ref: TableReference,
    col_name: str,
    *,
    read_version: int | None = None,
    concurrency: int = 8,
    batch_size: int | None = None,
    task_shuffle_diversity: int | None = None,
    commit_granularity: int | None = None,
    where: str | None = None,
    **kwargs,
) -> JobFuture:
    """
    Dispatch the Ray add column operation to a remote function.
    This is a convenience function to allow calling the remote function directly.
    """

    db = table_ref.open_db()
    hist = db._history
    job = hist.launch(table_ref.table_name, col_name, where=where, **kwargs)

    job_tracker = JobTracker.options(
        name=f"jobtracker-{job.job_id}",
        num_cpus=0.1,
        memory=128 * 1024 * 1024,
        max_restarts=-1,
    ).remote(job.job_id)

    obj_ref = run_ray_add_column_remote.remote(
        table_ref,
        col_name,
        read_version=read_version,
        job_id=job.job_id,
        job_tracker=job_tracker,
        concurrency=concurrency,
        batch_size=batch_size,
        task_shuffle_diversity=task_shuffle_diversity,
        commit_granularity=commit_granularity,
        where=where,
        **kwargs,
    )
    # object ref is only available here
    hist.set_object_ref(job.job_id, cloudpickle.dumps(obj_ref))
    return RayJobFuture(
        job_id=job.job_id,
        ray_obj_ref=obj_ref,
        job_tracker=job_tracker,
    )


def validate_backfill_args(
    tbl: Table,
    col_name: str,
    udf: UDF | None = None,
    input_columns: list[str] | None = None,
) -> None:
    """
    Validate the arguments for the backfill operation.
    This is a placeholder function to ensure that the arguments are valid.
    """
    if col_name not in tbl._ltbl.schema.names:
        raise ValueError(
            f"Column {col_name} is not defined this table.  "
            "Use add_columns to register it first"
        )

    if udf is None:
        from geneva.runners.ray.__main__ import fetch_udf

        udf_spec = fetch_udf(tbl, col_name)
        udf = tbl._conn._packager.unmarshal(udf_spec)

    if input_columns is None:
        field = tbl._ltbl.schema.field(col_name)
        input_columns = json.loads(
            field.metadata.get(b"virtual_column.udf_inputs", "null")
        )
    else:
        udf._input_columns_validator(None, input_columns)


@ray.remote
def run_ray_add_column_remote(
    table_ref: TableReference,
    col_name: str,
    *,
    job_id: str | None = None,
    input_columns: list[str] | None = None,
    udf: UDF | None = None,
    where: str | None = None,
    job_tracker: ActorHandle | None = None,
    **kwargs,
) -> None:
    """
    Remote function to run the Ray add column operation.
    This is a wrapper around `run_ray_add_column` to allow it to be called as a Ray
    task.
    """
    import geneva  # noqa: F401  Force so that we have the same env in next level down

    tbl = table_ref.open()
    hist = tbl._conn._history
    hist.set_running(job_id)
    try:
        validate_backfill_args(tbl, col_name, udf, input_columns)
        if udf is None:
            from geneva.runners.ray.__main__ import fetch_udf

            udf_spec = fetch_udf(tbl, col_name)
            udf = tbl._conn._packager.unmarshal(udf_spec)

        if input_columns is None:
            field = tbl._ltbl.schema.field(col_name)
            input_columns = json.loads(
                field.metadata.get(b"virtual_column.udf_inputs", "null")
            )

        from geneva.runners.ray.pipeline import run_ray_add_column

        checkpoint_store = tbl._conn._checkpoint_store
        run_ray_add_column(
            table_ref,
            input_columns,
            {col_name: udf},
            checkpoint_store=checkpoint_store,
            where=where,
            job_tracker=job_tracker,
            **kwargs,
        )
        hist.set_completed(job_id)
    except Exception as e:
        _LOG.exception("Error running Ray add column operation")
        hist.set_failed(job_id, str(e))
        raise e


def run_ray_add_column(
    table_ref: TableReference,
    columns: list[str] | None,
    transforms: dict[str, UDF],
    checkpoint_store: CheckpointStore | None = None,
    *,
    read_version: int | None = None,
    job_id: str | None = None,
    concurrency: int = 8,
    batch_size: int | None = None,
    task_shuffle_diversity: int | None = None,
    commit_granularity: int | None = None,
    where: str | None = None,
    job_tracker=None,
    **kwargs,
) -> None:
    # prepare job parameters
    config = JobConfig.get().with_overrides(
        batch_size=batch_size,
        task_shuffle_diversity=task_shuffle_diversity,
        commit_granularity=commit_granularity,
    )

    checkpoint_store = checkpoint_store or config.make_checkpoint_store()

    table = table_ref.open()
    uri = table.to_lance().uri

    # add pre-existing col if carrying previous values forward
    carry_forward_cols = list(set(transforms.keys()) & set(table.schema.names))
    _LOG.debug(f"carry_forward_cols {carry_forward_cols}")
    # this copy is necessary because the array extending updates inplace and this
    # columns array is directly referenced by the udf instance earlier
    cols = table.schema.names.copy() if columns is None else columns.copy()
    for cfcol in carry_forward_cols:
        # only append if cf col is not in col list already
        if cfcol not in cols:
            cols.append(cfcol)

    plan, pipeline_args = plan_read(
        uri,
        cols,
        batch_size=config.batch_size,
        read_version=read_version,
        task_shuffle_diversity=config.task_shuffle_diversity,
        where=where,
        **kwargs,
    )

    map_task = BackfillUDFTask(udfs=transforms, where=where)

    _LOG.info(
        f"starting backfill pipeline for {transforms} where='{where}'"
        f" with carry_forward_cols={carry_forward_cols}"
    )
    _run_column_adding_pipeline(
        map_task,
        checkpoint_store,
        config,
        table_ref,
        plan,
        job_id,
        concurrency,
        where=where,
        job_tracker=job_tracker,
        **pipeline_args,
    )


@attrs.define
class RayJobFuture(JobFuture):
    ray_obj_ref: ActorHandle = attrs.field()
    job_tracker: ActorHandle | None = attrs.field(default=None)
    _pbars: dict[str, TqdmType] = attrs.field(factory=dict)

    def _sync_bars(self, snapshot: dict[str, dict]) -> None:
        for name, m in snapshot.items():
            n, total, done, desc = m["n"], m["total"], m["done"], m.get("desc", name)
            bar = self._pbars.get(name)
            if bar is None:
                # Only make bars for the known core 4 (skip "fragments",
                # "writer_fragments", and other randoms)
                if name not in {
                    "workers",
                    "rows_checkpointed",
                    "rows_ready_for_commit",
                    "rows_committed",
                }:
                    continue
                bar = tqdm(total=total, desc=desc)
                self._pbars[name] = bar
            bar.total = total
            bar.n = n
            bar.refresh()
            if done:
                bar.close()

    def status(self) -> None:
        if self.job_tracker is None:
            return
        snapshot = ray.get(self.job_tracker.get_all.remote())
        self._sync_bars(snapshot)

    def done(self, timeout: float = 0.0) -> bool:
        self.status()
        _LOG.debug("Waiting for Ray job %s to complete", self.ray_obj_ref)
        ready, _ = ray.wait([self.ray_obj_ref], timeout=timeout)
        _LOG.debug("Ray jobs ready %s to complete", ready)
        done = bool(ready)
        if done:
            self.status()
        return done

    def result(self, timeout: float | None = None) -> Any:
        # TODO this can throw a ray.exceptions.GetTimeoutError if the task
        # does not complete in time, we should create a new exception type to
        # encapsulate Ray specifics
        self.status()
        return ray.get(self.ray_obj_ref, timeout=timeout)
