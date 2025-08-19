# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# a error logger for UDF jobs
import abc
import json
from collections.abc import Iterator
from typing import TYPE_CHECKING

import attrs
import pyarrow as pa

from geneva.checkpoint import CheckpointStore

if TYPE_CHECKING:
    from geneva.apply.task import ReadTask


class ErrorLogger(abc.ABC):
    @abc.abstractmethod
    def log_error(
        self,
        error: Exception,
        task: "ReadTask",
        seq: int,
    ) -> None: ...

    @abc.abstractmethod
    def list_errors(self) -> Iterator[str]: ...

    @abc.abstractmethod
    def get_error_row(self, error_id: str) -> pa.RecordBatch: ...


class NoOpErrorLogger(ErrorLogger):
    def log_error(
        self,
        error: Exception,
        task: "ReadTask",
        seq: int,
    ) -> None:
        pass

    def list_errors(self) -> Iterator[str]:
        return iter([])

    def get_error_row(self, error_id: str) -> pa.RecordBatch:
        raise KeyError(f"Error {error_id} not found")


@attrs.define
class CheckpointStoreErrorLogger(ErrorLogger):
    job_id: str = attrs.field()
    checkpoint_store: CheckpointStore = attrs.field()

    def _key(self, task: "ReadTask", seq: int) -> str:
        return f"{self.job_id}/{task.checkpoint_key()}-{seq}"

    def log_error(
        self,
        error: Exception,
        task: "ReadTask",
        seq: int,
    ) -> None:
        self.checkpoint_store[self._key(task, seq)] = pa.RecordBatch.from_pydict(
            {
                "error": [str(error)],
                "task": [json.dumps(attrs.asdict(task))],
                "seq": [seq],
            },
        )

    def list_errors(self) -> Iterator[str]:
        yield from self.checkpoint_store.list_keys(f"{self.job_id}/")

    def get_error_row(self, error_id: str) -> pa.RecordBatch:
        return self.checkpoint_store[f"{error_id}"]
