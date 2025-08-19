# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import base64
import logging
from pathlib import Path

import pytest

from geneva import connect

try:
    import ray  # noqa: F401

    from geneva.jobs import JobRecord, JobStateManager, JobStatus
except ImportError:
    pytest.skip("failed to import geneva.runners.ray", allow_module_level=True)


_LOG = logging.getLogger(__name__)


@pytest.fixture
def jobrecord() -> JobRecord:
    return JobRecord(table_name="test_table", column_name="test_column", config="{}")


def test_jobrecord(jobrecord) -> None:
    job = jobrecord
    assert job.job_id is not None
    assert job.table_name == "test_table"
    assert job.column_name == "test_column"
    assert job.config == "{}"
    assert job.status == JobStatus.PENDING
    assert job.object_ref is None


def test_jobstatemanager(tmp_path: Path) -> None:
    db = connect(tmp_path)
    jsm = JobStateManager(genevadb=db, jobs_table_name="test_jobs")

    tbl = db.open_table("test_jobs")  # Ensure the table is created
    assert tbl.count_rows() == 0
    _LOG.info(tbl.schema)

    tbl = jsm.jobs_table  # Ensure the table is created
    assert tbl.count_rows() == 0
    _LOG.info(tbl.schema)

    job = jsm.launch(
        table_name="test_table",
        column_name="test_column",
        arg1=1,
        arg2=0.0,
        arg3="test",
    )
    _LOG.info(job)
    job = jsm.get(job.job_id)[0]
    assert job.status == "PENDING"
    assert job.object_ref is None

    bad = jsm.get("nonexistent_job")
    assert len(bad) == 0

    jsm.set_running(job.job_id)
    job = jsm.get(job.job_id)[0]
    assert job.status == "RUNNING"
    assert job.object_ref is None

    b64_object_ref = base64.b64encode(b"xyz").decode("utf-8")
    jsm.set_object_ref(job.job_id, b"xyz")
    job = jsm.get(job.job_id)[0]
    assert job.object_ref == b64_object_ref

    jobs = jsm.list_active("test_table")
    assert len(jobs) == 1
    assert jobs[0].job_id == job.job_id
    assert jobs[0].status == "RUNNING"
    assert jobs[0].object_ref == b64_object_ref

    jsm.set_completed(job.job_id)
    job = jsm.get(job.job_id)[0]
    assert job.status == "DONE"
    assert job.object_ref == b64_object_ref
