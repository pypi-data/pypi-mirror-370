# ruff: noqa: PERF203

# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# super simple applier

import logging

import attrs
import pyarrow as pa

from geneva.apply.applier import BatchApplier
from geneva.apply.task import MapTask, ReadTask
from geneva.debug.logger import ErrorLogger

_LOG = logging.getLogger(__name__)


@attrs.define
class SimpleApplier(BatchApplier):
    """
    A simple applier that applies a function to each element in the batch.
    """

    def run(
        self,
        read_task: ReadTask,
        map_task: MapTask,
        error_logger: ErrorLogger,
    ) -> pa.RecordBatch:
        batches = []
        # TODO: add caching for the input data
        for seq, batch in enumerate(
            # TODO: allow configuring the global batch size via config
            read_task.to_batches(batch_size=map_task.batch_size())
        ):
            try:
                batches.append(map_task.apply(batch))
            except Exception as e:
                error_logger.log_error(e, read_task, seq)
                raise e
        if not batches:
            return pa.RecordBatch.from_arrays([])

        schema = batches[0].schema
        combined_table = pa.Table.from_batches(batches, schema)
        combined_table = combined_table.combine_chunks()
        combined_batch = combined_table.to_batches()[0]

        _LOG.info(
            f"Simple applier: completed {map_task} for {read_task} with"
            f" {len(combined_batch)} rows"
        )
        return combined_batch
