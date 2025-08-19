# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import functools
import logging
import os
from collections.abc import Callable
from typing import Any
from urllib.parse import urljoin

import attrs
import pyarrow as pa
import requests
from lancedb.common import Credential
from lancedb.remote.errors import LanceDBClientError
from pydantic import BaseModel
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from geneva.remote.timeout import LanceDBClientHTTPAdapterFactory

ARROW_STREAM_CONTENT_TYPE = "application/vnd.apache.arrow.stream"


def _read_ipc(resp: requests.Response) -> pa.Table:
    resp_body = resp.content
    with pa.ipc.open_file(pa.BufferReader(resp_body)) as reader:  # type: ignore
        return reader.read_all()


@attrs.define(slots=False, repr=True)
class RestfulLanceDBClient:
    db_name: str
    region: str
    api_key: Credential
    host_override: str | None = attrs.field(default=None)

    closed: bool = attrs.field(default=False, init=False)

    connection_timeout: float = attrs.field(default=120.0, kw_only=True)
    read_timeout: float = attrs.field(default=300.0, kw_only=True)

    @functools.cached_property
    def session(self) -> requests.Session:
        sess = requests.Session()

        retry_adapter_instance = retry_adapter(retry_adapter_options())
        sess.mount(urljoin(self.url, "/v1/table/"), retry_adapter_instance)

        adapter_class = LanceDBClientHTTPAdapterFactory()
        sess.mount("https://", adapter_class())
        return sess

    @property
    def url(self) -> str:
        return (
            self.host_override
            or f"https://{self.db_name}.{self.region}.api.lancedb.com"
        )

    def __enter__(self) -> "RestfulLanceDBClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.close()
        return False  # Do not suppress exceptions

    def close(self) -> None:
        self.session.close()
        self.closed = True

    @functools.cached_property
    def headers(self) -> dict[str, str | Credential]:
        headers: dict[str, str | Credential] = {
            "x-api-key": self.api_key,
        }
        if self.region == "local":  # Local test mode
            headers["Host"] = f"{self.db_name}.{self.region}.api.lancedb.com"
        if self.host_override:
            headers["x-lancedb-database"] = self.db_name
        return headers

    @staticmethod
    def _check_status(resp: requests.Response) -> None:
        # Leaving request id empty for now, as we'll be replacing this impl
        # with the Rust one shortly.
        if resp.status_code == 404:
            raise LanceDBClientError(
                f"Not found: {resp.text}", request_id="", status_code=404
            )
        elif 400 <= resp.status_code < 500:
            raise LanceDBClientError(
                f"Bad Request: {resp.status_code}, error: {resp.text}",
                request_id="",
                status_code=resp.status_code,
            )
        elif 500 <= resp.status_code < 600:
            raise LanceDBClientError(
                f"Internal Server Error: {resp.status_code}, error: {resp.text}",
                request_id="",
                status_code=resp.status_code,
            )
        elif resp.status_code != 200:
            raise LanceDBClientError(
                f"Unknown Error: {resp.status_code}, error: {resp.text}",
                request_id="",
                status_code=resp.status_code,
            )

    def get(
        self,
        path: str,
        params: dict[str, Any] | BaseModel | None = None,  # type: ignore
    ) -> str:
        """Send a GET request and returns the deserialized response payload."""
        if isinstance(params, BaseModel):
            params: dict[str, Any] = params.dict(exclude_none=True)
        with self.session.get(
            urljoin(self.url, path),
            params=params,
            headers=self.headers,
            timeout=(self.connection_timeout, self.read_timeout),
        ) as resp:
            self._check_status(resp)
            return resp.json()

    def post(
        self,
        uri: str,
        data: dict[str, Any] | BaseModel | bytes | None = None,  # type: ignore
        params: dict[str, Any] | None = None,
        content_type: str | None = None,
        deserialize: Callable = lambda resp: resp.json(),
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """Send a POST request and returns the deserialized response payload.

        Parameters
        ----------
        uri : str
            The uri to send the POST request to.
        data: Union[dict[str, Any], BaseModel]
        request_id: Optional[str]
            Optional client side request id to be sent in the request headers.

        """
        if isinstance(data, BaseModel):
            data: dict[str, Any] = data.dict(exclude_none=True)
        req_kwargs = {"data": data} if isinstance(data, bytes) else {"json": data}

        headers = self.headers.copy()
        if content_type is not None:
            headers["content-type"] = content_type
        if request_id is not None:
            headers["x-request-id"] = request_id
        with self.session.post(
            urljoin(self.url, uri),
            headers=headers,
            params=params,
            timeout=(self.connection_timeout, self.read_timeout),
            **req_kwargs,  # type: ignore
        ) as resp:
            self._check_status(resp)
            return deserialize(resp)

    def mount_retry_adapter_for_table(self, table_name: str) -> None:
        """
        Adds an http adapter to session that will retry retryable requests to the table.
        """
        retry_options = retry_adapter_options(methods=["GET", "POST"])
        retry_adapter_instance = retry_adapter(retry_options)
        session = self.session

        session.mount(
            urljoin(self.url, f"/v1/table/{table_name}/query/"), retry_adapter_instance
        )
        session.mount(
            urljoin(self.url, f"/v1/table/{table_name}/describe/"),
            retry_adapter_instance,
        )
        session.mount(
            urljoin(self.url, f"/v1/table/{table_name}/index/list/"),
            retry_adapter_instance,
        )


def retry_adapter_options(methods: list[str] | None = None) -> dict[str, Any]:
    if methods is None:
        methods = ["GET"]
    return {
        "retries": int(os.environ.get("LANCE_CLIENT_MAX_RETRIES", "3")),
        "connect_retries": int(os.environ.get("LANCE_CLIENT_CONNECT_RETRIES", "3")),
        "read_retries": int(os.environ.get("LANCE_CLIENT_READ_RETRIES", "3")),
        "backoff_factor": float(
            os.environ.get("LANCE_CLIENT_RETRY_BACKOFF_FACTOR", "0.25")
        ),
        "backoff_jitter": float(
            os.environ.get("LANCE_CLIENT_RETRY_BACKOFF_JITTER", "0.25")
        ),
        "statuses": [
            int(i.strip())
            for i in os.environ.get(
                "LANCE_CLIENT_RETRY_STATUSES", "429, 500, 502, 503"
            ).split(",")
        ],
        "methods": methods,
    }


def retry_adapter(options: dict[str, Any]) -> HTTPAdapter:
    total_retries = options["retries"]
    connect_retries = options["connect_retries"]
    read_retries = options["read_retries"]
    backoff_factor = options["backoff_factor"]
    backoff_jitter = options["backoff_jitter"]
    statuses = options["statuses"]
    methods = frozenset(options["methods"])
    logging.debug(
        f"Setting up retry adapter with {total_retries} retries,"  # noqa G003
        + f"connect retries {connect_retries}, read retries {read_retries},"
        + f"backoff factor {backoff_factor}, statuses {statuses}, "
        + f"methods {methods}"
    )

    return HTTPAdapter(
        max_retries=Retry(
            total=total_retries,
            connect=connect_retries,
            read=read_retries,
            backoff_factor=backoff_factor,
            backoff_jitter=backoff_jitter,
            status_forcelist=statuses,
            allowed_methods=methods,
        )
    )
