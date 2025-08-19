# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import itertools
import logging
import random
from collections.abc import Callable, Iterator, Mapping
from typing import TypeVar

import attrs
import lance
import more_itertools
import pyarrow as pa

from geneva.apply.applier import BatchApplier
from geneva.apply.simple import SimpleApplier
from geneva.apply.task import CopyTask, MapTask, ReadTask, ScanTask
from geneva.checkpoint import CheckpointStore
from geneva.debug.logger import ErrorLogger, NoOpErrorLogger
from geneva.table import TableReference

_LOG = logging.getLogger(__name__)


@attrs.define
class CheckpointingApplier:
    """
    Reads a read task and applies a map task to the data
    using a batch applier.

    The applier will checkpoint the output of the map task so that it can be
    resumed from the same point if the job is interrupted.
    """

    checkpoint_store: CheckpointStore = attrs.field()
    map_task: MapTask = attrs.field()

    error_logger: ErrorLogger = attrs.field(default=NoOpErrorLogger())
    batch_applier: BatchApplier = attrs.field(
        factory=SimpleApplier,
        converter=attrs.converters.default_if_none(factory=SimpleApplier),
    )

    @property
    def output_schema(self) -> pa.Schema:
        return self.map_task.output_schema()

    def _run(self, task: ReadTask) -> str:
        data_key = task.checkpoint_key()
        _LOG.info("Running task %s", task)
        # track the batch sequence number so we can checkpoint any errors
        # when reproducing locally we can seek to the erroring batch quickly

        checkpoint_key = f"{data_key}:{self.map_task.checkpoint_key()}"
        if checkpoint_key in self.checkpoint_store:
            _LOG.info("Using cached result for %s", checkpoint_key)
            return checkpoint_key

        batch = self.batch_applier.run(
            task,
            self.map_task,
            error_logger=self.error_logger,
        )

        self.checkpoint_store[checkpoint_key] = batch
        _LOG.info(f"checkpointed key={checkpoint_key}")
        return checkpoint_key

    def run(self, task: ReadTask) -> str:
        try:
            return self._run(task)
        except Exception as e:
            logging.exception("Error running task %s: %s", task, e)
            raise RuntimeError(f"Error running task {task}") from e

    def status(self, task: ReadTask) -> bool:
        data_key = task.checkpoint_key()
        return f"{data_key}:{self.map_task.checkpoint_key()}" in self.checkpoint_store


def _plan_read(
    uri: str,
    columns: list[str],
    *,
    read_version: int | None = None,
    batch_size: int = 512,
    where: str | None = None,
    num_frags: int | None = None,
) -> Iterator[ReadTask]:
    """Make Plan for Reading Data from a Dataset
    We want a ScanTask for each fragment in the dataset even if they are filtered
    out. This should make the checkpointing recovery easier to manage.
    """
    dataset = lance.dataset(uri)
    if read_version is not None:
        dataset = dataset.checkout_version(read_version)

    # get_fragments has an unsupported filter method, so we do filtering deeper in.
    for idx, frag in enumerate(dataset.get_fragments()):
        if num_frags is not None and idx >= num_frags:
            break

        frag_rows = frag.count_rows()
        filtered_frag_rows = frag.count_rows(filter=where)
        if filtered_frag_rows == 0:
            _LOG.debug(
                f"frag {frag.fragment_id} filtered by '{where}' has no rows, skipping."
            )
            continue

        _LOG.debug(
            f"plan_read fragment: {frag} has {frag_rows} rows, filtered to"
            f" {filtered_frag_rows} rows"
        )
        for offset in range(0, frag_rows, batch_size):
            limit = min(batch_size, frag_rows - offset)
            _LOG.debug(
                f"scan task: idx={idx} fragid={frag.fragment_id} offset={offset} "
                f"limit={limit} where={where}"
            )
            yield ScanTask(
                uri=uri,
                version=read_version,
                columns=columns,
                frag_id=frag.fragment_id,
                offset=offset,
                limit=limit,
                where=where,
                with_row_address=True,
            )


T = TypeVar("T")  # Define type variable "T"


@attrs.define
class _LanceReadPlanIterator(Iterator[T]):
    it: Iterator[T]
    total: int

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        return next(self.it)

    def __len__(self) -> int:
        return self.total


def _num_tasks(
    *,
    uri: str,
    read_version: int | None = None,
    batch_size: int = 512,
) -> int:
    return sum(
        -(-frag.count_rows() // batch_size)
        for frag in (lance.dataset(uri, version=read_version)).get_fragments()
    )


T = TypeVar("T")


def _buffered_shuffle(it: Iterator[T], buffer_size: int) -> Iterator[T]:
    """Shuffle an iterator using a buffer of size buffer_size
    not perfectly random, but good enough for spreading out IO
    """
    # Initialize the buffer with the first buffer_size items from the iterator
    buffer = []
    # Fill the buffer with up to buffer_size items initially
    try:
        for _ in range(buffer_size):
            item = next(it)
            buffer.append(item)
    except StopIteration:
        pass

    while True:
        # Select a random item from the buffer
        index = random.randint(0, len(buffer) - 1)
        item = buffer[index]

        # Try to replace the selected item with a new one from the iterator
        try:
            next_item = next(it)
            buffer[index] = next_item
            # Yield the item AFTER replacing it in the buffer
            # this way the buffer is always contiguous so we can
            # simply yield the buffer at the end
            yield item
        except StopIteration:
            yield from buffer
            break


R = TypeVar("R")


def diversity_aware_shuffle(
    it: Iterator[T],
    key: Callable[[T], R],
    *,
    diversity_goal: int = 4,
    buffer_size: int = 1024,
) -> Iterator[T]:
    """A shuffle iterator that is aware of the diversity of the data
    being shuffled. The key function should return a value that is
    is used to determine the diversity of the data. The diversity_goal
    is the number of unique values that should be in the buffer at any
    given time. if the buffer is full, the items is yielded in a round-robin
    fashion. This is useful for shuffling tasks that are diverse, but

    This algorithm is bounded in memory by the buffer_size, so it is reasonably
    efficient for large datasets.
    """

    # NOTE: this is similar to itertools.groupby, but with a buffering limit

    buffer: dict[R, list[T]] = {}
    buffer_total_size = 0

    peekable_it = more_itertools.peekable(it)

    def _maybe_consume_from_iter() -> bool:
        nonlocal buffer_total_size
        item = peekable_it.peek(default=None)
        if item is None:
            return False
        key_val = key(item)
        if key_val not in buffer and len(buffer) < diversity_goal:
            buffer[key_val] = []
        else:
            return False

        # if the buffer still has room, add the item
        if buffer_total_size < buffer_size:
            buffer[key_val].append(item)
            buffer_total_size += 1
        else:
            return False

        next(peekable_it)
        return True

    while _maybe_consume_from_iter():
        ...

    production_counter = 0

    def _next_key() -> T | None:
        nonlocal buffer_total_size, production_counter
        if not buffer_total_size:
            return None

        # TODO: add warning about buffer size not big enough for diversity_goal
        buffer_slot = production_counter % len(buffer)
        key = next(itertools.islice(buffer.keys(), buffer_slot, buffer_slot + 1))
        assert key in buffer
        key_buffer = buffer[key]

        buffer_total_size -= 1
        item = key_buffer.pop(0)
        if not key_buffer:
            del buffer[key]

        # try to fill the removed buffer slot
        _maybe_consume_from_iter()
        production_counter += 1
        return item

    while (item := _next_key()) is not None:
        yield item


def plan_read(
    uri: str,
    columns: list[str],
    *,
    read_version: int | None = None,
    batch_size: int = 512,
    where: str | None = None,
    shuffle_buffer_size: int = 0,
    task_shuffle_diversity: int | None = None,
    num_frags: int | None = None,
    **unused_kwargs,
) -> tuple[Iterator[ReadTask], Mapping]:
    """
    Make Plan for Reading Data from a Dataset

    Parameters
    ----------
    num_frags:
        max number of fragments to scan for sampling use cases.
    """
    it = _plan_read(
        uri,
        columns=columns,
        read_version=read_version,
        batch_size=batch_size,
        where=where,
        num_frags=num_frags,
    )
    # same as no shuffle
    if shuffle_buffer_size > 1 and task_shuffle_diversity is None:
        it = _buffered_shuffle(it, buffer_size=shuffle_buffer_size)
    elif task_shuffle_diversity is not None:
        buffer_size = max(4 * task_shuffle_diversity, shuffle_buffer_size)
        it = diversity_aware_shuffle(
            it,
            key=lambda task: task.checkpoint_key(),
            diversity_goal=task_shuffle_diversity,
            buffer_size=buffer_size,
        )

    return _LanceReadPlanIterator(
        it, _num_tasks(uri=uri, read_version=read_version, batch_size=batch_size)
    ), unused_kwargs


def _plan_copy(
    src: TableReference,
    dst: TableReference,
    columns: list[str],
    *,
    batch_size: int = 512,
) -> tuple[Iterator[CopyTask], int]:
    """Make Plan for Reading Data from a Dataset"""
    dst_dataset = dst.open().to_lance()
    num_tasks = 0
    for frag in dst_dataset.get_fragments():
        frag_rows = frag.count_rows()
        # ceil_div
        num_tasks += -(frag_rows // -batch_size)

    def task_gen() -> Iterator[CopyTask]:
        for frag in dst_dataset.get_fragments():
            frag_rows = frag.count_rows()
            for offset in range(0, frag_rows, batch_size):
                limit = min(batch_size, frag_rows - offset)
                yield CopyTask(
                    src=src,
                    dst=dst,
                    columns=columns,
                    frag_id=frag.fragment_id,
                    offset=offset,
                    limit=limit,
                )

    return (task_gen(), num_tasks)


def plan_copy(
    src: TableReference,
    dst: TableReference,
    columns: list[str],
    *,
    batch_size: int = 512,
    shuffle_buffer_size: int = 0,
    task_shuffle_diversity: int | None = None,
) -> Iterator[CopyTask]:
    (it, num_tasks) = _plan_copy(
        src,
        dst,
        columns,
        batch_size=batch_size,
    )
    # same as no shuffle
    if shuffle_buffer_size > 1 and task_shuffle_diversity is None:
        it = _buffered_shuffle(it, buffer_size=shuffle_buffer_size)
    elif task_shuffle_diversity is not None:
        buffer_size = max(4 * task_shuffle_diversity, shuffle_buffer_size)
        it = diversity_aware_shuffle(
            it,
            key=lambda task: task.checkpoint_key(),
            diversity_goal=task_shuffle_diversity,
            buffer_size=buffer_size,
        )

    return _LanceReadPlanIterator(it, num_tasks)
