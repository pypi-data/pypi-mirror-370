# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import hashlib
import json
import logging
import platform
from collections.abc import Iterable, Iterator
from datetime import timedelta
from functools import cached_property
from typing import Any, Literal, Union, overload

import attrs
import lance
import lancedb
import numpy as np
import pyarrow as pa
from lancedb.common import VEC, VECTOR_COLUMN_NAME
from lancedb.index import IndexConfig
from lancedb.query import FullTextQuery, LanceQueryBuilder, LanceTakeQueryBuilder
from lancedb.query import Query as LanceQuery
from lancedb.table import IndexStatistics, TableStatistics, Tags
from lancedb.table import LanceTable as LanceLocalTable
from lancedb.table import Table as LanceTable
from lancedb.types import QueryType
from pyarrow.fs import FileSystem, LocalFileSystem

# Python 3.10 compatibility
from typing_extensions import Never, override  # noqa: UP035
from yarl import URL

from geneva.checkpoint import (
    CheckpointStore,
    InMemoryCheckpointStore,
    LanceCheckpointStore,
)
from geneva.db import Connection, connect
from geneva.query import GenevaQueryBuilder
from geneva.transformer import UDF

_LOG = logging.getLogger(__name__)


@attrs.define
class JobFuture:
    job_id: str

    def done(self, timeout: float = 0) -> bool:
        raise NotImplementedError("JobFuture.done() must be implemented in subclasses")

    def result(self, timeout: float | None = None) -> Any:
        raise NotImplementedError(
            "JobFuture.result() must be implemented in subclasses"
        )

    def status(self) -> None:
        raise NotImplementedError(
            "JobFuture.status() must be implemented in subclasses"
        )


@attrs.define(order=True)
class TableReference:
    """
    Serializable reference to a Geneva Table.

    Used to pass through ray.remote calls
    """

    db_uri: str
    table_name: str
    version: int | None

    def open_checkpoint_store(self) -> CheckpointStore:
        """Open a Lance checkpoint store for this table."""
        try:
            return LanceCheckpointStore(str(URL(str(self.db_uri)) / "ckp"))
        except Exception:
            # Fallback to in-memory checkpoint store if Lance store fails
            return InMemoryCheckpointStore()

    def open_db(self) -> Connection:
        """Open a connection to the Lance database.
        Set read consistency interval to 0 for strongly consistent reads."""
        return connect(
            self.db_uri,
            checkpoint=self.open_checkpoint_store(),
            read_consistency_interval=timedelta(0),
        )

    def open(self) -> "Table":
        return self.open_db().open_table(self.table_name, version=self.version)


class Table(LanceTable):
    """Table in Geneva.

    A Table is a Lance dataset
    """

    def __init__(
        self,
        conn: Connection,
        name: str,
        *,
        version: int | None = None,
        storage_options: dict[str, str] | None = None,
        index_cache_size: int | None = None,
        **kwargs,
    ) -> None:
        self._conn_uri = conn.uri
        self._name = name

        self._conn = conn

        base_uri = URL(conn.uri)
        self._uri = str(base_uri / f"{name}.lance")
        self._version: int | None = version
        self._index_cache_size = index_cache_size
        self._storage_options = storage_options

        # Load table
        self._ltbl  # noqa

    def __repr__(self) -> str:
        return f"<Table {self._name}>"

    # TODO: This annotation sucks
    def __reduce__(self):  # noqa: ANN204
        return (self.__class__, (self._conn, self._name))

    def get_reference(self) -> TableReference:
        return TableReference(
            db_uri=self._conn.uri, table_name=self._name, version=self._version
        )

    def get_fragments(self) -> list[lance.LanceFragment]:
        return self.to_lance().get_fragments()

    @cached_property
    def _ltbl(self) -> lancedb.table.Table:
        # remote db, open table directly
        if self._conn_uri.startswith("db://"):
            tbl = self._conn._connect.open_table(self._name)
            if self._version:
                tbl.checkout(self._version)
            return tbl

        return self._conn._connect.open_table(self.name)

    @property
    def name(self) -> str:
        """Get the name of the table."""
        return self._name

    @property
    def version(self) -> int:
        """Get the current version of the table"""
        return self._ltbl.version

    @property
    def schema(self) -> pa.Schema:
        """The Arrow Schema of the Table."""
        return self._ltbl.schema

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def embedding_functions(self) -> Never:
        raise NotImplementedError("Embedding functions are not supported.")

    def add(
        self,
        data,
        mode: str = "append",
        on_bad_vectors: str = "error",
        fill_value: float = 0.0,
    ) -> None:
        self._ltbl.add(
            data,
            mode=mode,
            on_bad_vectors=on_bad_vectors,
            fill_value=fill_value,
        )

    def checkout(self, version: int) -> None:
        self._version = version
        self._ltbl.checkout(version)

    def checkout_latest(self) -> None:
        self._ltbl.checkout_latest()

    def add_columns(
        self, transforms: dict[str, str | UDF | tuple[UDF, list[str]]], *args, **kwargs
    ) -> None:
        """
        Add columns or udf based columns to the Geneva table.

        Parameters
        ----------
        transforms : dict[str, str | UDF | tuple[UDF, list[str]]]
            The key is the column name to add and the value is a
            specification of the column type/value.
            * If the spec is a string, it is expected to be a datafusion
              sql expression. (e.g "cast(null as string)"))
            * If the spec is a UDF, a virtual column is added with input
              columns inferred from the UDF's argument names.
            * If the spec is a tuple, the first element is a UDF and the
              second element is a list of input column names.

        Raises
        ------
        ValueError

        """
        # handle basic columns
        basic_cols = {k: v for k, v in transforms.items() if isinstance(v, str)}
        if len(basic_cols) > 0:
            self._ltbl.add_columns(basic_cols, *args)

        # handle UDF virtual columns
        udf_cols = {k: v for k, v in transforms.items() if not isinstance(v, str)}
        for k, v in udf_cols.items():
            if isinstance(v, UDF):
                # infer column names from udf arguments
                udf = v
                self._add_virtual_columns(
                    {k: udf}, *args, input_columns=udf.input_columns, **kwargs
                )
            else:
                # explicitly specify input columns
                (udf, cols) = v
                self._add_virtual_columns({k: udf}, *args, input_columns=cols, **kwargs)

    def _add_virtual_columns(
        self,
        mapping: dict[str, UDF],  # this breaks the non udf mapping
        *args,
        input_columns: list[str] | None = None,
        **kwargs,
    ) -> None:
        """
        This is an internal method and not intended to be called directly.

        Add udf based virtual columns to the Geneva table.
        """

        if len(mapping) != 1:
            raise ValueError("Only one UDF is supported for now.")

        _LOG.info("Adding column: udf=%s", mapping)
        col_name = next(iter(mapping))
        udf = mapping[col_name]

        if not isinstance(udf, UDF):
            # Stateful udfs are implemenated as Callable classses, and look
            # like partial functions here.  Instantiate to get the return
            # data_type annotations.
            udf = udf()
        self._ltbl.add_columns(pa.field(col_name, udf.data_type))
        self._configure_virtual_column(col_name, udf, input_columns)

    def refresh(self, where: str | None = None) -> None:
        """
        Refresh the specified materialized view.

        Parameters
        ----------
        where: str | None
            TODO: sql expression filter used to only backfill selected rows
        """
        if where:
            raise NotImplementedError(
                "where clauses on materialized view refresh not implemented yet."
            )

        from geneva.runners.ray.pipeline import run_ray_copy_table

        run_ray_copy_table(
            self.get_reference(), self._conn._packager, self._conn._checkpoint_store
        )
        self.checkout_latest()

    def backfill_async(
        self,
        col_name: str,
        *,
        input_columns: list[str] | None = None,
        udf: UDF | None = None,
        where: str | None = None,
        **kwargs,
    ) -> JobFuture:
        """Run backfill asynchronously by dispatching a driver task."""
        from geneva.runners.ray.pipeline import (
            dispatch_run_ray_add_column,
            validate_backfill_args,
        )

        validate_backfill_args(self, col_name, udf, input_columns)

        fut = dispatch_run_ray_add_column(
            self.get_reference(),
            col_name,
            udf=udf,
            input_columns=input_columns,
            where=where,
            **kwargs,
        )
        return fut

    def backfill(
        self,
        col_name,
        *,
        input_columns: list[str] | None = None,
        udf: UDF | None = None,
        where: str | None = None,
        concurrency: int = 8,
        intra_applier_concurrency: int = 1,
        refresh_status_secs: float = 2.0,
        **kwargs,
    ) -> str:
        """
        Backfills the specified column.

        Returns job_id string

        Parameters
        ----------
        col_name: str
            Target column name to backfill
        input_columns: list[str] | None
            Optionally override columns used as sources for scalar UDF input arguments
            or pa.Array batch UDF arguments.  Not valid for pa.RecordBatch UDFs.
        udf: UDF | None
            Optionally override the UDF used to backfill the column.
        where: str | None
            SQL expression filter used select rows to apply backfills.
        concurrency: int
            (default = 8) This controls the number of processes that tasks run
            concurrently. For max throughput, ideally this is larger than the number
            of nodes in the k8s cluster.   This is the number of Ray actor processes
            are started.
        intra_applier_concurrency: int
            (default = 1) This controls the number of threads used to execute tasks
            within a process. Multiplying this times `concurrency` roughly corresponds
            to the number of cpu's being used.
        commit_granularity: int | None
            (default = 64) Show a partial result everytime this number of fragments
            are completed. If None, the entire result is committed at once.
        read_version: int | None
            (default = None) The version of the table to read from.  If None, the
            latest version is used.
        task_shuffle_diversity: int | None
            (default = 8) ??
        batch_size: int | None
            (default = 10240) The number of rows per batch when reading data from the
            table. If None, the default value is used.

        """
        # Input validation
        from geneva.runners.ray.pipeline import validate_backfill_args

        validate_backfill_args(self, col_name, udf, input_columns)

        # get cluster status
        from geneva.runners.ray.raycluster import ClusterStatus

        cs = ClusterStatus()
        cs.get_status()

        # Kick off the job
        fut = self.backfill_async(
            col_name,
            input_columns=input_columns,
            udf=udf,
            where=where,
            concurrency=concurrency,
            intra_applier_concurrency=intra_applier_concurrency,
            **kwargs,
        )

        while not fut.done(timeout=refresh_status_secs):
            # wait for the backfill to complete, updating statuses
            cs.get_status()
            fut.status()

        cs.get_status()
        fut.status()

        # updates came from an external writer, so get the latest version.
        self._ltbl.checkout_latest()
        return fut.job_id

    def alter_columns(self, *alterations: Iterable[dict[str, Any]], **kwargs) -> None:
        """
        Alter columns in the table.  This can change the computed columns' udf

        Parameters
        ----------
        alterations:  Iterable[dict[str, Any]]
            This is a list of alterations to apply to the table.


        Example:
            >>> alter_columns({ "path": "col1", "udf": col1_udf_v2, })`
            >>> t.alter_columns(b
            ...     { "path": "col1", "udf": col1_udf_v2, },
            ...     { "path": "col2", "udf": col2_udf})

        """
        basic_column_alterations = []
        for alter in alterations:
            if "path" not in alter:
                raise ValueError("path is required to alter computed column's udf")

            if "virtual_column" in alter:  # deprecated
                if not isinstance(alter.get("virtual_column"), UDF):
                    raise ValueError("virtual_column must be a UDF")
                udf = alter.get("virtual_column")
                _LOG.warning(
                    "alter_columns 'virtual_column' is deprecated, use 'udf' instead."
                )
            elif "udf" in alter:
                if not isinstance(alter.get("udf"), UDF):
                    raise ValueError("udf must be a UDF")
                udf = alter.get("udf")
            else:
                basic_column_alterations.append(alter)
                continue

            col_name = alter["path"]

            input_cols = alter.get("input_columns", None)
            if input_cols is None:
                input_cols = udf.input_columns

            self._configure_virtual_column(col_name, udf, input_cols)

        if len(basic_column_alterations) > 0:
            self._ltbl.alter_columns(*basic_column_alterations)

    def _configure_virtual_column(
        self,
        col_name: str,
        udf: UDF,
        input_cols: list[str] | None,
    ) -> None:
        """
        Configure a column to be a virtual column for the given UDF.

        This procedure includes:
        - Packaging the UDF
        - Uploading the UDF to the dataset
        - Updating the field metadata to include the UDF information

        Note that the column should already exist on the table.
        """
        udf_spec = self._conn._packager.marshal(udf)

        # upload the UDF to the dataset URL
        if not isinstance(self._ltbl, LanceLocalTable):
            raise TypeError(
                "adding udf column is currently only supported for local tables"
            )

        # upload the packaged UDF to some location inside the dataset:
        ds = self.to_lance()
        fs, root_uri = FileSystem.from_uri(ds.uri)
        checksum = hashlib.sha256(udf_spec.udf_payload).hexdigest()
        udf_location = f"_udfs/{checksum}"

        # TODO -- only upload the UDF if it doesn't exist
        if isinstance(fs, LocalFileSystem):
            # Object storage filesystems like GCS and S3 will create the directory
            # automatically, but local filesystem will not, so we create explicitly
            fs.create_dir(f"{root_uri}/_udfs")

        with fs.open_output_stream(f"{root_uri}/{udf_location}") as f:
            f.write(udf_spec.udf_payload)

        field_metadata = udf.field_metadata | {
            "virtual_column": "true",
            "virtual_column.udf_backend": udf_spec.backend,
            "virtual_column.udf_name": udf_spec.name,
            "virtual_column.udf": "_udfs/" + checksum,
            "virtual_column.udf_inputs": json.dumps(input_cols),
            "virtual_column.platform.system": platform.system(),
            "virtual_column.platform.arch": platform.machine(),
            "virtual_column.platform.python_version": platform.python_version(),
        }

        # Add the column metadata:
        self._ltbl.replace_field_metadata(col_name, field_metadata)

    def create_index(
        self,
        metric: str = "L2",
        num_partitions: int | None = None,
        num_sub_vectors: int | None = None,
        vector_column_name: str = VECTOR_COLUMN_NAME,
        replace: bool = True,
        accelerator=None,
        index_cache_size=None,
        *,
        index_type: Literal[
            "IVF_FLAT",
            "IVF_PQ",
            "IVF_HNSW_SQ",
            "IVF_HNSW_PQ",
        ] = "IVF_PQ",
        num_bits: int = 8,
        max_iterations: int = 50,
        sample_rate: int = 256,
        m: int = 20,
        ef_construction: int = 300,
    ) -> None:
        """Create Vector Index"""
        self._ltbl.create_index(
            metric,
            num_partitions or 256,
            num_sub_vectors or 96,
            vector_column_name,
            replace,
            accelerator,
            index_cache_size,
            index_type=index_type,
            num_bits=num_bits,
            max_iterations=max_iterations,
            sample_rate=sample_rate,
            m=m,
            ef_construction=ef_construction,
        )

    @override
    def create_fts_index(
        self,
        field_names: str | list[str],
        *,
        ordering_field_names: str | list[str] | None = None,
        replace: bool = False,
        writer_heap_size: int | None = None,
        tokenizer_name: str | None = None,
        with_position: bool = True,
        base_tokenizer: Literal["simple", "raw", "whitespace"] = "simple",
        language: str = "English",
        max_token_length: int | None = 40,
        lower_case: bool = True,
        stem: bool = False,
        remove_stop_words: bool = False,
        ascii_folding: bool = False,
        **_kwargs,
    ) -> None:
        self._ltbl.create_fts_index(
            field_names,
            ordering_field_names=ordering_field_names,
            replace=replace,
            writer_heap_size=writer_heap_size,
            tokenizer_name=tokenizer_name,
            with_position=with_position,
            base_tokenizer=base_tokenizer,
            language=language,
            max_token_length=max_token_length,
            lower_case=lower_case,
            stem=stem,
            remove_stop_words=remove_stop_words,
            ascii_folding=ascii_folding,
            use_tantivy=False,
        )

    @override
    def create_scalar_index(
        self,
        column: str,
        *,
        replace: bool = True,
        index_type: Literal["BTREE", "BITMAP", "LABEL_LIST"] = "BTREE",
    ) -> None:
        self._ltbl.create_scalar_index(
            column,
            replace=replace,
            index_type=index_type,
        )

    @override
    def _do_merge(self, other: "Table", on: list[str], how: str) -> Never:
        raise NotImplementedError("Merging tables is not supported.")

    @override
    def _execute_query(
        self,
        query: LanceQuery,
        batch_size: int | None = None,
    ) -> pa.RecordBatchReader:
        return self._ltbl._execute_query(query, batch_size=batch_size)

    def list_versions(self) -> list[dict[str, Any]]:
        return self._ltbl.list_versions()

    @override
    def cleanup_old_versions(
        self,
        older_than: timedelta | None = None,
        *,
        delete_unverified=False,
    ) -> "lance.CleanupStats":
        return self._ltbl.cleanup_old_versions(
            older_than,
            delete_unverified=delete_unverified,
        )

    def to_batches(self, batch_size: int | None = None) -> Iterator[pa.RecordBatch]:
        from .query import Query

        if isinstance(self._ltbl, Query):
            return self._ltbl.to_batches(batch_size)
        return self.to_lance().to_batches(batch_size)

    @overload
    def search(
        self,
        query: Union[VEC, str, "PIL.Image.Image", tuple, FullTextQuery],  # noqa: F821
        vector_column_name: str | None = None,
        query_type: QueryType = "auto",
        ordering_field_name: str | None = None,
        fts_columns: str | list[str] | None = None,
    ) -> LanceQueryBuilder: ...

    """This is the signature for the standard LanceDB table.search call"""

    def search(
        self,
        query: list | pa.Array | pa.ChunkedArray | np.ndarray | None = None,
        vector_column_name: str | None = None,
        query_type: Literal["vector", "fts", "hybrid", "auto"] = "auto",
        ordering_field_name: str | None = None,
        fts_columns: str | list[str] | None = None,
    ) -> GenevaQueryBuilder:
        if query is None:
            return GenevaQueryBuilder(self)
        else:
            return self._ltbl.search(
                query, vector_column_name, query_type, ordering_field_name, fts_columns
            )

    @override
    def drop_columns(self, columns: Iterable[str]) -> None:
        self._ltbl.drop_columns(columns)

    @override
    def to_arrow(self) -> pa.Table:
        return self._ltbl.to_arrow()

    @override
    def count_rows(self, filter: str | None = None) -> int:
        return self._ltbl.count_rows(filter)

    @override
    def update(
        self,
        where: str | None = None,
        values: dict | None = None,
        *,
        values_sql: dict[str, str] | None = None,
    ) -> None:
        self._ltbl.update(where, values, values_sql=values_sql)

    @override
    def delete(self, where: str) -> None:
        self._ltbl.delete(where)

    @override
    def list_indices(self) -> Iterable[IndexConfig]:
        return self._ltbl.list_indices()

    @override
    def index_stats(self, index_name: str) -> IndexStatistics | None:
        return self._ltbl.index_stats(index_name)

    @override
    def optimize(
        self,
        *,
        cleanup_older_than: timedelta | None = None,
        delete_unverified: bool = False,
    ) -> None:
        return self._ltbl.optimize(
            cleanup_older_than=cleanup_older_than,
            delete_unverified=delete_unverified,
        )

    @override
    def compact_files(self) -> None:
        self._ltbl.compact_files()

    @override
    def restore(self, *args, **kwargs) -> None:
        self._ltbl.restore(*args, **kwargs)

    # TODO: This annotation sucks
    def take_blobs(self, indices: list[int] | pa.Array, column: str):  # noqa: ANN201
        return self.to_lance().take_blobs(indices, column)

    def to_lance(self) -> lance.LanceDataset:
        return self._ltbl.to_lance()

    def uses_v2_manifest_paths(self) -> bool:
        return self._ltbl.uses_v2_manifest_paths()

    def migrate_v2_manifest_paths(self) -> None:
        return self._ltbl.migrate_v2_manifest_paths()

    def _analyze_plan(self, query: lancedb.query.Query) -> str:
        return self._ltbl._analyze_plan(query)

    def _explain_plan(
        self, query: lancedb.query.Query, verbose: bool | None = False
    ) -> str:
        return self._ltbl._explain_plan(query, verbose=verbose)

    def stats(self) -> TableStatistics:
        return self._ltbl.stats()

    @property
    def tags(self) -> Tags:
        return self._ltbl.tags

    def take_offsets(self, offsets: list[int]) -> LanceTakeQueryBuilder:
        return self._ltbl.take_offsets(offsets)

    def take_row_ids(self, row_ids: list[int]) -> LanceTakeQueryBuilder:
        return self._ltbl.take_row_ids(row_ids)
