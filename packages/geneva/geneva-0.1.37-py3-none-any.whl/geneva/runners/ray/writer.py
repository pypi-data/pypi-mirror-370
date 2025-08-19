# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import logging
import os
import urllib
import urllib.parse
import uuid
from collections.abc import Iterator
from typing import cast

import attrs
import lance
import lance.file
import pyarrow as pa
import ray
import ray.actor
import ray.util.queue
from yarl import URL

from geneva.checkpoint import CheckpointStore
from geneva.utils.parse_rust_debug import extract_field_ids
from geneva.utils.sequence_queue import SequenceQueue

_LOG = logging.getLogger(__name__)


def _fill_rowaddr_gaps(batch: pa.RecordBatch) -> pa.RecordBatch:
    """
    This fills the gaps in the _rowaddr column of the batch.
    It assumes that the _rowaddr column is present and sorted.
    It will fill in the gaps with None values for other columns.

    example: start with rowaddr [1, 3], values [10, 30]
    returns rowaddr [1, 2, 3], values [10, None, 30]
    """

    if "_rowaddr" not in batch.schema.names:
        raise ValueError(
            "No _rowaddr column found in the batch,"
            " please make sure the scanner is configured with with_row_address=True"
        )

    rowaddr: pa.Array = batch["_rowaddr"]

    rowaddr_start = rowaddr[0].as_py()
    rowaddr_end = rowaddr[-1].as_py()

    num_physical_rows_in_range = rowaddr_end - rowaddr_start + 1

    if num_physical_rows_in_range == batch.num_rows:
        return batch

    # TODO: this is inefficient in python, do it in rust
    data_dict = {
        "_rowaddr": pa.array(range(rowaddr_start, rowaddr_end + 1), type=pa.uint64()),
    }
    for name in batch.schema.names:
        if name == "_rowaddr":
            continue

        arr = batch[name]

        def _iter(name=name):  # noqa: ANN202
            next_idx = rowaddr_start
            for val, row_addr in zip(
                batch[name].to_pylist(), rowaddr.to_pylist(), strict=False
            ):
                while next_idx < row_addr:
                    yield None
                    next_idx += 1
                yield val
                next_idx += 1

        data_dict[name] = pa.array(_iter(), type=arr.type)

    return batch.from_pydict(data_dict, schema=batch.schema)


def _buffer_and_sort_batches(
    num_logical_rows: int,
    store: CheckpointStore,
    queue: ray.util.queue.Queue,
) -> Iterator[pa.RecordBatch]:
    """
    buffer batches from the queue, which is yields a tuple of
    * serial number of the batch -- currently the offset of the batch
    * the data key dict of the batch

    serial number can arrive out of order, so we need to buffer them
    until we have the next expected serial number. In most cases, the
    serial number is the offset of the batch, and we keep track of the
    expected serial number in the variable `written_rows`
    """
    accumulation_queue = SequenceQueue()
    rows_returned = 0
    while rows_returned < num_logical_rows:
        # Pump the input until we have the next batch
        while (
            accumulation_queue.next_position() < num_logical_rows
            and accumulation_queue.is_empty()
        ):
            try:
                batch: tuple[int, str] = queue.get()
            except (
                ray.exceptions.ActorDiedError,
                ray.exceptions.ActorUnavailableError,
            ):
                _LOG.exception("Writer failed to read from checkpoint queue, exiting")
                ray.actor.exit_actor()
                return  # Unreachable, but makes pyright happy

            checkpoint_key = batch[1]

            stored = store[checkpoint_key]
            accumulation_queue.put(batch[0], stored.num_rows, stored)

        # Return the next batch (and any other freed batches)
        while not accumulation_queue.is_empty():
            batch = accumulation_queue.pop()
            yield batch
            rows_returned += batch.num_rows


def _make_filler_batch(
    fill_start: int,
    fill_end: int,
    schema: pa.Schema,
) -> pa.RecordBatch:
    """
    make a batch that fills the range [fill_start, fill_end) with None values
    for all columns except _rowaddr, which will be filled with the range.
    Note: fill_end is exclusive, so the batch will have (fill_end - fill_start) rows.
    """
    _LOG.info(f"Filling range: {fill_start} -- {fill_end}")
    rowaddr_arr = pa.array(range(fill_start, fill_end), type=pa.uint64())
    data_dict = {
        name: pa.array([None] * (fill_end - fill_start), type=schema.field(name).type)
        for name in schema.names
        if name != "_rowaddr"
    }
    data_dict["_rowaddr"] = rowaddr_arr
    return pa.RecordBatch.from_pydict(data_dict, schema=schema)


def _align_batches_to_physical_layout(
    num_physical_rows: int,
    num_logical_rows: int,
    frag_id: int,
    batches: Iterator[pa.RecordBatch],
) -> Iterator[pa.RecordBatch]:
    """
    This aligns the batches to the physical rows layout.

    It will fill in the _rowaddr gaps within a batch with new rows with the _rowaddr
    index values and None values for the other columns.  It will also fill the _rowaddr
    gaps between batches with the _rowaddr index values and None values for the other
    cols.
    """

    if num_logical_rows > num_physical_rows:
        raise ValueError(
            "Logical rows should be greater than or equal to physical rows"
        )

    next_batch_rowaddr = 0

    schema = None

    for batch in map(
        _fill_rowaddr_gaps,
        batches,
    ):
        # skim the schema from the stream
        # we expect at least one batch, otherwise the whole fragment has been
        # deleted and the metadata would have been deleted by lance so we wouldn't
        # be here because no writer would be created
        if schema is None:
            schema = batch.schema

        incoming_local_rowaddr = batch["_rowaddr"][0].as_py() & 0xFFFFFFFF
        if incoming_local_rowaddr != next_batch_rowaddr:
            # global row id has frag_id in high bits
            fill_start = frag_id << 32 | next_batch_rowaddr
            fill_end = frag_id << 32 | incoming_local_rowaddr
            yield _make_filler_batch(fill_start, fill_end, schema)
            next_batch_rowaddr = incoming_local_rowaddr

        yield batch
        next_batch_rowaddr += batch.num_rows

    if schema is None:
        raise ValueError("No batches found")

    # fill the rest of the rows at the end
    if next_batch_rowaddr < num_physical_rows:
        fill_start = frag_id << 32 | next_batch_rowaddr
        fill_end = frag_id << 32 | num_physical_rows
        yield _make_filler_batch(fill_start, fill_end, schema)


@ray.remote(num_cpus=1)
@attrs.define
class FragmentWriter:
    uri: str
    column_names: list[str]
    store: CheckpointStore

    fragment_id: int

    checkpoint_keys: ray.util.queue.Queue

    where: str | None = None

    # frag id, new_file, rows_written
    def write(self) -> tuple[int, lance.fragment.DataFile, int]:
        _LOG.debug(
            f"Writing fragment {self.fragment_id} to {self.uri} with columns"
            f" {self.column_names} where '{self.where}'"
        )
        dataset = lance.dataset(self.uri)
        frag = dataset.get_fragment(self.fragment_id)
        if frag is None:
            _LOG.warning(f"Fragment {self.fragment_id} not found in dataset {self.uri}")
            raise ValueError(f"Fragment {self.fragment_id} not found")
        num_physical_rows = frag.physical_rows  # num rows before deletions
        num_logical_rows = frag.count_rows()  # num rows including filters/deletions

        import more_itertools

        # we always write files that physically align with the fragment
        it = _buffer_and_sort_batches(
            num_logical_rows,
            self.store,
            self.checkpoint_keys,
        )

        it = _align_batches_to_physical_layout(
            num_physical_rows,
            num_logical_rows,
            self.fragment_id,
            it,
        )

        it = more_itertools.peekable(it)

        file_id = str(uuid.uuid4())
        path = str(URL(self.uri) / "data" / f"{file_id}.lance")
        if not urllib.parse.urlparse(self.uri).scheme:
            path = f"file://{os.path.abspath(path)}"

        written = 0
        schema = it.peek().schema
        with lance.file.LanceFileWriter(path, schema) as writer:
            for batch in it:
                writer.write_batch(batch)
                written += batch.num_rows

        field_ids = []
        for column_name in self.column_names:
            field_ids.extend(extract_field_ids(dataset.lance_schema, column_name))

        _LOG.debug(
            f"writing fragment file {file_id}.lance with cols:{self.column_names} "
        )
        new_datafile = lance.fragment.DataFile(
            f"{file_id}.lance",
            field_ids,
            list(range(len(field_ids))),
            2,  # major version
            0,  # minor version
        )

        return self.fragment_id, new_datafile, written


FragmentWriter: ray.actor.ActorClass = cast("ray.actor.ActorClass", FragmentWriter)
