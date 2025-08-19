# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# A simple port forwarder for talking to ray head
# this is for testing only, and should NEVER be used in production

import logging
import select
import socket
import threading

import attrs
import kubernetes
import kubernetes.stream.ws_client
from typing_extensions import Self

from geneva.runners.ray.raycluster import RayCluster

_LOG = logging.getLogger(__name__)


@attrs.define
class _Flag:
    val: bool
    lock: threading.Lock = attrs.field(factory=threading.Lock, init=False)

    @classmethod
    def true(cls) -> Self:
        return cls(True)

    def __bool__(self) -> bool:
        with self.lock:
            return self.val

    def set(self, val: bool) -> None:
        with self.lock:
            self.val = val


@attrs.define
class PortForward:
    """
    A simple port forwarder for talking to a k8s pod

    This forwarder binds and listens on a local port. Any traffic
    sent to this port is forwarded to the specified pod and port.

    Note: when local_port is 0, a random port will be allocated by the OS
    and the local port will be set to that value. User is responsible
    for checking the local port value after the forwarder is started.
    """

    pod_name: str
    namespace: str
    port: int
    core_api: kubernetes.client.CoreV1Api

    local_port: int = 0

    alive: _Flag = attrs.field(factory=_Flag.true, init=False)

    threads: list[threading.Thread] = attrs.field(factory=list, init=False)

    proxy_start_barrier: threading.Barrier = attrs.field(init=False)

    proxy_listener: socket.socket = attrs.field(init=False)

    @classmethod
    def to_head_node(
        cls,
        cluster: RayCluster,
    ) -> Self:
        pod = cluster.head_node_pod

        # TODO: allocate a random local port
        return cls(
            pod_name=pod.metadata.name,
            namespace=cluster.namespace,
            core_api=cluster.core_api,
            port=10001,
        )

    def _start_proxy(
        self,
        pod_socket: socket.socket,
        client_socket: socket.socket,
    ) -> None:
        _LOG.debug("Starting proxy from pod to client")
        proxy_thread = threading.Thread(
            target=_proxy,
            args=(pod_socket, client_socket, self.alive),
        )
        self.threads.extend([proxy_thread])
        proxy_thread.start()

        _LOG.debug("Proxy started")

    def _start_listener_loop(self) -> None:
        _LOG.debug("Starting listener loop")
        proxy_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_listener.bind(("localhost", self.local_port))
        if self.local_port == 0:
            self.local_port = proxy_listener.getsockname()[1]
        proxy_listener.listen()

        self.proxy_listener = proxy_listener

        self.proxy_start_barrier.wait()

        while self.alive:
            _LOG.debug("Waiting for client connection")
            try:
                client_socket, _ = proxy_listener.accept()
            except OSError:
                # socket is closed, exit
                _LOG.warning("Listener socket closed")
                break
            client_socket.setblocking(True)

            forward: kubernetes.stream.ws_client.PortForward = (
                kubernetes.stream.portforward(
                    self.core_api.connect_get_namespaced_pod_portforward,
                    self.pod_name,
                    self.namespace,
                    ports=f"{self.port}",
                )
            )

            pod_socket = forward.socket(self.port)
            pod_socket.setblocking(True)

            self._start_proxy(pod_socket, client_socket)

    def __enter__(self) -> Self:
        _LOG.debug("Starting port forward")
        self.alive.set(True)
        self.proxy_start_barrier = threading.Barrier(2)
        listener_thread = threading.Thread(
            target=self._start_listener_loop,
        )
        self.threads.append(listener_thread)
        listener_thread.start()

        self.proxy_start_barrier.wait()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        _LOG.debug("Stopping port forward")
        self.alive.set(False)

        # not a clean shutdown, but we don't care
        try:
            self.proxy_listener.shutdown(socket.SHUT_RDWR)
        except Exception:
            _LOG.exception("error stopping portforward")

        for thread in self.threads:
            thread.join(timeout=1)

        self.threads.clear()
        _LOG.debug("Port forward stopped")


def _format_sock(sock: socket.socket) -> str:
    """Return a short from "host:port" to "host:port" description, or fallback to
    type name."""
    try:
        laddr = sock.getsockname()
        raddr = sock.getpeername()
        return f"{laddr[0]}:{laddr[1]} <-> {raddr[0]}:{raddr[1]}"
    except Exception:
        return f"<{type(sock).__name__}>"


def _proxy(
    s1: socket.socket,
    s2: socket.socket,
    alive=True,
    *,
    buffer_size: int = 4096,
) -> None:
    _LOG.info(f"Proxying between {_format_sock(s1)} and {_format_sock(s2)}")
    while alive:
        for s in select.select([s1, s2], [], [])[0]:
            data = s.recv(buffer_size)
            {s1: s2, s2: s1}[s].sendall(data)
