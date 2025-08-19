# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# Job Management

from enum import Enum, unique
from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from geneva.job.client import JobClient


@unique
class JobStatus(Enum):
    """Status of a Job"""

    PENDING = 1
    RUNNING = 2
    COMPLETED = 3
    FAILED = 4


@attrs.define
class Job:
    """A Feature Engineering Job.

    User should not directly construct this object.
    """

    db: str = attrs.field()

    table: str = attrs.field()

    job_id: str = attrs.field()

    version: int | None = attrs.field(default=None)

    status: JobStatus | None = attrs.field(init=False, default=None)

    # TODO: it is possible to generate multiple columns if the output type
    # is a struct / record batch.
    column: str | list[str] = attrs.field(init=False, default=None)
    input_columns: list[str] = attrs.field(init=False, default=None)

    # Packaging information
    docker_image: str | None = attrs.field(default=None)
    udf_uri: str | None = attrs.field(default=None)

    # Runner info
    dataflow_job_id: str | None = attrs.field(default=None, repr=False)

    # Control runtime parameters
    limit: int | None = attrs.field(default=None)
    offset: int | None = attrs.field(default=None)
    filter: str | None = attrs.field(default=None)

    _client: "JobClient" = attrs.field(init=False, default=None, repr=False)

    def __attr_post_init__(self) -> None:
        # TODO: init client, fetch job info if not provided
        pass

    def __repr__(self) -> str:
        return f"Job(id={self.job_id})"

    def start(self) -> None: ...

    def stop(self) -> None: ...
