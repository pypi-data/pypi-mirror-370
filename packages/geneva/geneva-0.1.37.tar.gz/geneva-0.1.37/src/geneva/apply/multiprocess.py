# ruff: noqa: PERF203
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# multi-process applier

import io
from typing import Literal

import attrs
import multiprocess
import pyarrow as pa

import geneva.cloudpickle as cloudpickle
from geneva.apply.applier import BatchApplier
from geneva.apply.task import MapTask, ReadTask
from geneva.debug.logger import ErrorLogger


def _buf_to_batch(
    data: bytes | memoryview,
    *,
    coalesce: bool = False,
) -> list[pa.RecordBatch] | pa.RecordBatch:
    """
    Convert a buffer to a record batch.
    """
    buf = io.BytesIO(data)
    with pa.ipc.open_stream(buf) as f:
        t = f.read_all()
    if not coalesce:
        return t.to_batches()
    else:
        return t.combine_chunks().to_batches()[0]


def _batch_to_buf(
    batch: pa.RecordBatch,
) -> bytes:
    """
    Convert a record batch to a buffer.
    """
    buf = io.BytesIO()
    with pa.ipc.new_stream(buf, schema=batch.schema) as f:
        f.write_batch(batch)
    buf.seek(0)
    return buf.getvalue()


def _apply_with_stream_buf(
    apply: bytes,
    buf: bytes,
) -> bytes:
    """
    Apply a function to a record batch using a stream buffer.
    """
    func = cloudpickle.loads(apply)
    out_buf = io.BytesIO()
    out_batches = [func(batch) for batch in _buf_to_batch(buf)]
    with pa.ipc.new_stream(out_buf, schema=out_batches[0].schema) as f:
        for batch in out_batches:
            f.write_batch(batch)

    return out_buf.getvalue()


@attrs.define
class MultiProcessBatchApplier(BatchApplier):
    """
    A multi-process applier that applies a function to each element in the batch.
    """

    num_processes: int = attrs.field(validator=attrs.validators.ge(1))

    method: Literal["fork", "spawn"] = attrs.field(default="fork")

    def run(
        self,
        read_task: ReadTask,
        map_task: MapTask,
        error_logger: ErrorLogger,
    ) -> pa.RecordBatch:
        ctx = (
            multiprocess.context.ForkContext()
            if self.method == "fork"
            else multiprocess.context.SpawnContext()
        )

        with ctx.Pool(self.num_processes) as pool:
            # don't pull new batches until the previous ones are done
            # this way we reduce the number of batches in memory
            def _run_with_backpressure():  # noqa: ANN202
                futs = []
                seqs = []

                for seq, batch in enumerate(
                    read_task.to_batches(batch_size=map_task.batch_size())
                ):
                    # TODO: allow configuring the global batch size via config
                    seqs.append(seq)
                    data = _batch_to_buf(batch)
                    udf_data = cloudpickle.dumps(map_task.apply)

                    futs.append(
                        pool.apply_async(_apply_with_stream_buf, args=(udf_data, data))
                    )
                    # don't start waiting till we have primed the queue
                    if len(futs) >= self.num_processes + 1:
                        seq = seqs.pop(0)
                        fut = futs.pop(0)
                        try:
                            yield _buf_to_batch(fut.get(), coalesce=True)
                        except Exception as e:
                            error_logger.log_error(e, read_task, seq)
                            raise e

                while futs:
                    seq = seqs.pop(0)
                    fut = futs.pop(0)
                    try:
                        yield _buf_to_batch(fut.get(), coalesce=True)
                    except Exception as e:
                        error_logger.log_error(e, read_task, seq)
                        raise e

            batches = list(_run_with_backpressure())

            if not batches:
                return pa.RecordBatch.from_arrays([])

            schema = batches[0].schema
            combined_table = pa.Table.from_batches(batches, schema)
            combined_table = combined_table.combine_chunks()
            combined_batch = combined_table.to_batches()[0]

            return combined_batch
