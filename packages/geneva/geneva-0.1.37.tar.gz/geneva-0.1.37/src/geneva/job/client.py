# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

"""Job History Client"""

from collections.abc import Iterable

from geneva.job import Job
from geneva.remote.client import RestfulLanceDBClient


class JobClient:
    """Job History Client"""

    def __init__(self, rest_client: RestfulLanceDBClient) -> None:
        self.rest_client = rest_client

    def list(
        self,
        *,
        table: str | None = None,
        _columns: str | list[str] | None = None,
        _limit: int = 100,
        _offset: int = 0,
    ) -> Iterable[dict]:
        """Get the ID of the Jobs which satisfy the given conditions."""
        req = {"table": table} if table else {}
        resp = self.rest_client.post("/v1/job/list/", data=req)
        yield from resp["jobs"]

    def get_job(self, job_id: str) -> Job: ...

    def upsert_job(self, job: Job) -> None: ...

    def start(
        self,
        table: str,
        column: str,
    ) -> None:
        """Start a new job."""
        self.rest_client.post(
            "/v1/job/start/",
            data={
                "job": {
                    "materialize_virtual_column": {
                        "columns": [column],
                        "table": table,
                    }
                }
            },
            deserialize=lambda x: x,
        )
