# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import base64
import enum
import json
import logging
import uuid
from datetime import datetime
from enum import Enum, unique

import attrs

from geneva.db import Connection
from geneva.utils import dt_now_utc, retry_on_exception
from geneva.utils.arrow import schema_from_attrs

GENEVA_JOBS_TABLE_NAME = "geneva_jobs"

_LOG = logging.getLogger(__name__)


@unique
class JobStatus(Enum):
    """Status of a Job"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


@attrs.define
class JobRecord:
    """A Feature Engineering Job record.

    When a backfill or refresh is triggered, these records contain the job's details for
    history tracking and also provides references for jobs if they are still running
    so other users can track it.

    User should not directly construct this object.
    """

    table_name: str = attrs.field()
    column_name: str = attrs.field()
    job_id: str = attrs.field(factory=lambda: str(uuid.uuid4()))
    job_type: str = attrs.field(default="BACKFILL")
    object_ref: str = attrs.field(default=None)
    status: JobStatus = attrs.field(default=JobStatus.PENDING)
    launched_at: datetime = attrs.field(factory=lambda: dt_now_utc())
    completed_at: datetime = attrs.field(default=None)
    config: str = attrs.field(default="{}")


class JobStateManager:
    def __init__(
        self, genevadb: Connection, jobs_table_name=GENEVA_JOBS_TABLE_NAME
    ) -> None:
        self.jobs_db = genevadb
        try:
            self.jobs_table = self.jobs_db.open_table(jobs_table_name)
        except ValueError:
            # If the table does not exist, or has a schema problem, just (re)create it
            # TODO we need to make this a schema evolution case.
            self.jobs_table = self.jobs_db.create_table(
                jobs_table_name, schema=schema_from_attrs(JobRecord), mode="overwrite"
            )

    @retry_on_exception(max_attempts=3, initial_delay=1, backoff_factor=2)
    def launch(self, table_name: str, column_name: str, **kwargs) -> JobRecord:
        args = kwargs.copy()
        args.pop("udf", None)  # Remove the udf argument (TODO serialized it)
        jr = JobRecord(
            table_name=table_name,
            column_name=column_name,
            config=json.dumps(args),
        )
        self.jobs_table.add(
            [
                attrs.asdict(
                    jr,
                    value_serializer=lambda obj, a, v: v.value
                    if isinstance(v, enum.Enum)
                    else v,
                )
            ]
        )
        return jr

    @retry_on_exception(max_attempts=3, initial_delay=1, backoff_factor=2)
    def set_object_ref(self, job_id: str, object_ref: bytes) -> None:
        self.jobs_table._ltbl.update(
            where=f"job_id = '{job_id}'",
            # TODO why can't lance handle bytes in an update directly?
            values={
                "object_ref": base64.b64encode(object_ref).decode("utf-8"),
            },
        )

    def _set_status(self, job_id: str, status: JobStatus) -> None:
        self.jobs_table._ltbl.update(
            where=f"job_id = '{job_id}'",
            values={
                "status": status.value,
            },
        )

    @retry_on_exception(max_attempts=3, initial_delay=1, backoff_factor=2)
    def set_running(self, job_id: str) -> None:
        self._set_status(job_id, JobStatus.RUNNING)

    @retry_on_exception(max_attempts=3, initial_delay=1, backoff_factor=2)
    def set_failed(self, job_id: str, msg: str) -> None:
        # TODO add msg to the record
        self._set_status(job_id, JobStatus.FAILED)

    def list_active(self, table_name: str | None = None) -> list[JobRecord]:
        # TODO: Currently need to use tbl._ltbl.search() instead of tbl.search()
        # because geneva table semantics are not consistent with lancedb's currently
        wheres = ["status == 'RUNNING'"]
        if table_name:
            wheres.append(f"table_name = '{table_name}'")
        jrs = (
            self.jobs_table._ltbl.search()
            .where(" and ".join(wheres))
            .to_arrow()
            .to_pylist()
        )
        return [JobRecord(**jr) for jr in jrs]

    def get(self, job_id: str) -> list[JobRecord]:
        # TODO: Currently need to use tbl._ltbl.search() instead of tbl.search()
        # because geneva table semantics are not consistent with lancedb's currently

        # Need to get latest because updates can come from othe processes
        self.jobs_table._ltbl.checkout_latest()
        q = self.jobs_table._ltbl.search().where(f"job_id = '{job_id}'")
        return [JobRecord(**jr) for jr in q.to_arrow().to_pylist()]

    @retry_on_exception(max_attempts=3, initial_delay=1, backoff_factor=2)
    def set_completed(self, job_id: str, status: str = "DONE") -> None:
        self.jobs_table._ltbl.update(
            where=f"job_id = '{job_id}'",
            values={
                "status": status,
                "completed_at": dt_now_utc(),
            },
        )
