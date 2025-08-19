import random
from pathlib import Path

import pyarrow as pa

try:
    import ray
    import ray.util.queue

    from geneva.runners.ray.writer import (
        _align_batch_to_row_address,
        _align_batches_to_physical_layout,
        _buffer_and_sort_batches,
    )
except ImportError:
    import pytest

    pytest.skip("failed to import ray", allow_module_level=True)

from geneva.checkpoint import LanceCheckpointStore


def test_align_batch_to_row_address_no_alignment_needed() -> None:
    batch = pa.RecordBatch.from_arrays(
        [pa.array([1, 2, 3, 4], type=pa.uint64())], names=["_rowaddr"]
    )

    assert _align_batch_to_row_address(batch) == batch


def test_align_batch_to_row_address_alignment_needed() -> None:
    range1, range_2 = random.randint(0, 1024), random.randint(0, 1024)
    start = min(range1, range_2)
    end = max(range1, range_2)

    batch = pa.RecordBatch.from_arrays(
        [pa.array([start, end], type=pa.uint64())], names=["_rowaddr"]
    )

    assert _align_batch_to_row_address(batch) == pa.RecordBatch.from_arrays(
        [pa.array(range(start, end + 1), type=pa.uint64())], names=["_rowaddr"]
    )


def test_buffer_sort_and_align_batches_no_alignment_needed(
    tmp_path: Path,
) -> None:
    batch1 = pa.RecordBatch.from_arrays(
        [pa.array(range(16), type=pa.uint64()), pa.array(range(16), type=pa.uint64())],
        names=["data", "_rowaddr"],
    )

    batch2 = pa.RecordBatch.from_arrays(
        [
            pa.array(range(16, 32), type=pa.uint64()),
            pa.array(range(16, 32), type=pa.uint64()),
        ],
        names=["data", "_rowaddr"],
    )

    store = LanceCheckpointStore(tmp_path.as_posix())

    store["batch1"] = batch1
    store["batch2"] = batch2

    queue = ray.util.queue.Queue()
    queue.put(
        (
            16,
            "batch2",
        )
    )
    queue.put(
        (
            0,
            "batch1",
        )
    )

    assert list(
        _align_batches_to_physical_layout(
            32,
            32,
            0,
            _buffer_and_sort_batches(
                32,
                store,
                queue,
            ),
        )
    ) == [
        pa.RecordBatch.from_arrays(
            [
                pa.array(range(16), type=pa.uint64()),
                pa.array(range(16), type=pa.uint64()),
            ],
            names=["data", "_rowaddr"],
        ),
        pa.RecordBatch.from_arrays(
            [
                pa.array(range(16, 32), type=pa.uint64()),
                pa.array(range(16, 32), type=pa.uint64()),
            ],
            names=["data", "_rowaddr"],
        ),
    ]


def test_buffer_sort_and_align_batches_alignment_needed(
    tmp_path: Path,
) -> None:
    batch1 = pa.RecordBatch.from_arrays(
        [
            pa.array(range(0, 16, 2), type=pa.uint64()),
            pa.array(range(0, 16, 2), type=pa.uint64()),
        ],
        names=["data", "_rowaddr"],
    )

    batch2 = pa.RecordBatch.from_arrays(
        [
            pa.array(range(16, 32, 2), type=pa.uint64()),
            pa.array(range(16, 32, 2), type=pa.uint64()),
        ],
        names=["data", "_rowaddr"],
    )

    store = LanceCheckpointStore(tmp_path.as_posix())

    store["batch1"] = batch1
    store["batch2"] = batch2

    queue = ray.util.queue.Queue()
    queue.put(
        (
            8,
            "batch2",
        )
    )
    queue.put(
        (
            0,
            "batch1",
        )
    )

    batches = list(
        _align_batches_to_physical_layout(
            64,
            16,
            0,
            _buffer_and_sort_batches(
                16,
                store,
                queue,
            ),
        )
    )

    assert pa.Table.from_batches(batches).combine_chunks().to_batches() == [
        pa.RecordBatch.from_arrays(
            [
                pa.array(
                    [i if i % 2 == 0 else None for i in range(32)] + [None] * 32,
                    type=pa.uint64(),
                ),
                pa.array(range(64), type=pa.uint64()),
            ],
            names=["data", "_rowaddr"],
        )
    ]
