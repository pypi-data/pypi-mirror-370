# type: ignore

# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# This module contains an adapter that will close connections if they have not been
# used before a certain timeout. This is necessary because some load balancers will
# close connections after a certain amount of time, but the request module may not yet
# have received the FIN/ACK and will try to reuse the connection.
#
# TODO some of the code here can be simplified if/when this PR is merged:
# https://github.com/urllib3/urllib3/pull/3275


import datetime
import logging
import os

from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPSConnection
from urllib3.connectionpool import HTTPSConnectionPool
from urllib3.poolmanager import PoolManager

from geneva.utils import dt_now_utc


def get_client_connection_timeout() -> int:
    return int(os.environ.get("LANCE_CLIENT_CONNECTION_TIMEOUT", "300"))


class LanceDBHTTPSConnection(HTTPSConnection):
    """
    HTTPSConnection that tracks the last time it was used.
    """

    idle_timeout: datetime.timedelta
    last_activity: datetime.datetime

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.last_activity = dt_now_utc()

    def request(self, *args, **kwargs) -> None:
        self.last_activity = dt_now_utc()
        super().request(*args, **kwargs)

    def is_expired(self) -> bool:
        return dt_now_utc() - self.last_activity > self.idle_timeout


def LanceDBHTTPSConnectionPoolFactory(client_idle_timeout: int):  # noqa: ANN201, N802
    """
    Creates a connection pool class that can be used to close idle connections.
    """

    class LanceDBHTTPSConnectionPool(HTTPSConnectionPool):
        # override the connection class
        ConnectionCls = LanceDBHTTPSConnection

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

        def _get_conn(self, timeout: float | None = None):  # noqa: ANN202
            logging.debug("Getting https connection")
            conn = super()._get_conn(timeout)
            if conn.is_expired():
                logging.debug("Closing expired connection")
                conn.close()

            return conn

        def _new_conn(self):  # noqa: ANN202
            conn = super()._new_conn()
            conn.idle_timeout = datetime.timedelta(seconds=client_idle_timeout)
            return conn

    return LanceDBHTTPSConnectionPool


class LanceDBClientPoolManager(PoolManager):
    def __init__(
        self, client_idle_timeout: int, num_pools: int, maxsize: int, **kwargs
    ) -> None:
        super().__init__(num_pools=num_pools, maxsize=maxsize, **kwargs)
        # inject our connection pool impl
        connection_pool_class = LanceDBHTTPSConnectionPoolFactory(
            client_idle_timeout=client_idle_timeout
        )
        self.pool_classes_by_scheme["https"] = connection_pool_class


def LanceDBClientHTTPAdapterFactory():  # noqa: ANN201, N802
    """
    Creates an HTTPAdapter class that can be used to close idle connections
    """

    # closure over the timeout
    client_idle_timeout = get_client_connection_timeout()

    class LanceDBClientRequestHTTPAdapter(HTTPAdapter):
        def init_poolmanager(self, connections, maxsize, block=False) -> None:
            # inject our pool manager impl
            self.poolmanager = LanceDBClientPoolManager(
                client_idle_timeout=client_idle_timeout,
                num_pools=connections,
                maxsize=maxsize,
                block=block,
            )

    return LanceDBClientRequestHTTPAdapter
