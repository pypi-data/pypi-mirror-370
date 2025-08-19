# ruff: noqa: F821

# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# For managing and launching Ray Cluster

import abc
import contextlib
import enum
import functools
import getpass
import json
import logging
import platform
import re
import sys
import time
from collections import Counter
from collections.abc import Generator, Iterable, Iterator
from typing import Any, TypeVar

import attrs
import kubernetes
import kubernetes.client.exceptions
import ray
import yaml

# do global config init
from kubernetes.client.api import scheduling_v1_api

from geneva.config import ConfigBase
from geneva.eks import K8sConfigMethod, build_api_client
from geneva.runners.ray.kuberay import _k8s_status, _ray_status
from geneva.tqdm import tqdm

_LOG = logging.getLogger(__name__)

GENEVA_RAY_HEAD_NODE = "geneva.lancedb.com/ray-head"
GENEVA_RAY_CPU_NODE = "geneva.lancedb.com/ray-worker-cpu"
GENEVA_RAY_GPU_NODE = "geneva.lancedb.com/ray-worker-gpu"

CPU_ONLY_NODE = "cpu-only"


@attrs.define
class _RayClusterConfig(ConfigBase):
    user: str = attrs.field(
        converter=attrs.converters.default_if_none(default=getpass.getuser())
    )

    namespace: str = attrs.field(
        converter=attrs.converters.default_if_none(default="geneva")
    )

    @classmethod
    def name(cls) -> str:
        return "raycluster"

    def cluster_name(self) -> str:
        if self.user:
            return self.user
        _LOG.info("Using the current OS user name as the cluster name")
        return getpass.getuser()


def _size_converter(value: int | str) -> int:
    if isinstance(value, int):
        return value
    suffixes = {
        "K": 1000,
        "M": 1000**2,
        "G": 1000**3,
        "T": 1000**4,
        "Ki": 1024,
        "Mi": 1024**2,
        "Gi": 1024**3,
        "Ti": 1024**4,
    }
    match = re.match(r"(?P<value>\d+)(?P<unit>[KMGT]i?)", value)
    value = int(match.group("value"))
    unit = suffixes[match.group("unit")]

    return value * unit


class _ValidationVisitable(abc.ABC):
    @abc.abstractmethod
    def _validate(self, visitor: "_ValidationVisitor") -> None:
        """
        Validate at cluster construction time if the definition is valid
        """


@attrs.define(kw_only=True, slots=False)
class _ResourceMixin:
    num_cpus: int = attrs.field(default=1, validator=attrs.validators.gt(0))
    memory: int = attrs.field(
        converter=_size_converter,
        default=3 * (1024**3),
        validator=attrs.validators.gt(0),
    )
    num_gpus: int = attrs.field(default=0, validator=attrs.validators.ge(0))

    arm: bool = attrs.field(default=platform.processor() in {"aarch64", "arm"})

    @property
    def _resources(self) -> dict:
        resource = {
            "requests": {
                "cpu": self.num_cpus,
                "memory": self.memory,
            },
            "limits": {
                "cpu": self.num_cpus,
                "memory": self.memory,
            },
        }

        if self.num_gpus:
            resource["requests"]["nvidia.com/gpu"] = self.num_gpus
            resource["limits"]["nvidia.com/gpu"] = self.num_gpus

        return resource


@attrs.define(kw_only=True, slots=False)
class _ServiceAccountMixin(_ValidationVisitable):
    service_account: str | None = attrs.field(default=None)

    @property
    def _service_account(self) -> dict[str, str] | None:
        if self.service_account is None:
            return None
        return {
            "serviceAccountName": self.service_account,
        }

    def _validate(self, visitor: "_ValidationVisitor") -> None:
        visitor.visit_service_account(self)


@attrs.define(kw_only=True, slots=False)
class _PriorityClassMixin(_ValidationVisitable):
    priority_class: str | None = attrs.field(default=None)

    @property
    def _priority_class(self) -> dict[str, str] | None:
        if self.priority_class is None:
            return None
        return {
            "priorityClassName": self.priority_class,
        }

    def _validate(self, visitor: "_ValidationVisitor") -> None:
        visitor.visit_priority_class(self)


@attrs.define(kw_only=True, slots=False)
class _RayVersionMixin:
    ray_version: str = attrs.field(init=False)
    """
    The version of Ray to use for the cluster. Auto detected from the Ray
    package version in the current environment.
    """

    @ray_version.default
    def _default_ray_version(self) -> str:
        return ray.__version__


@attrs.define(kw_only=True, slots=False)
class _PythonVersionMixin:
    python_version: str = attrs.field(init=False)
    """
    The major.minor version of Python to use for the cluster.
    Auto detected from the python version in the current environment.
    """

    @python_version.default
    def _default_python_version(self) -> str:
        return f"{sys.version_info.major}.{sys.version_info.minor}"


def get_ray_image(
    version: str, python_version: str, *, gpu: bool = False, arm: bool = False
) -> str:
    py_version = python_version.replace(".", "")
    image = f"rayproject/ray:{version}-py{py_version}"
    if gpu:
        image += "-gpu"
    if arm:
        # todo: is this needed? ray provides multi-platform images
        image += "-aarch64"
    return image


@attrs.define(kw_only=True, slots=False)
class _ImageMixin(_RayVersionMixin, _PythonVersionMixin, _ResourceMixin):
    # set a dummpy default so the generated __init__
    # gets the correct signature
    image: str = attrs.field()

    @image.default
    def _default_image(self) -> str:
        return get_ray_image(
            self.ray_version,
            self.python_version,
            gpu=self.num_gpus > 0,
            arm=self.arm,
        )

    def _validate(self, visitor: "_ValidationVisitor") -> None:
        visitor.visit_image(self)


@attrs.define(kw_only=True, slots=False)
class _MountsMixin:
    volumes: dict[str, dict] = attrs.field(default={})
    """
    Volumes to attach to the worker Pod.

    The key is the name of the volume and the value is the volume specification.
    """

    mounts: list[tuple[str, str]] = attrs.field(default=[])
    """
    The list of mounts to attach to the worker containers.
    """

    @mounts.validator
    def _validate_mounts(self, attribute: str, value: list[tuple[str, str]]) -> None:
        paths = set()
        for name, path in value:
            if name not in self.volumes:
                raise ValueError(f"Volume {name} not found in volumes")
            paths.add(path)

        if len(paths) != len(value):
            dups = [
                item
                for item, count in Counter(path for _, path in value).items()
                if count > 1
            ]
            raise ValueError(f"Duplicate mount paths: {dups}")

    @property
    def mounts_definition(self) -> list[dict[str, str]]:
        return [{"name": volume, "mountPath": path} for volume, path in self.mounts]

    @property
    def volume_definition(self) -> list[dict[str, str]]:
        return [{"name": volume, **config} for volume, config in self.volumes.items()]


class _PodSpec(
    _ImageMixin,
    _ResourceMixin,
    _MountsMixin,
    _ServiceAccountMixin,
    _PriorityClassMixin,
    _ValidationVisitable,
):
    def _validate(self, visitor: "_ValidationVisitor") -> None:
        visitor.visit_service_account(self)
        visitor.visit_priority_class(self)
        visitor.visit_image(self)


@attrs.define(kw_only=True)
class _HeadGroupSpec(_PodSpec):
    node_selector: dict[str, str] = attrs.field(default={"_PLACEHOLDER": "true"})

    def __attrs_post_init__(self) -> None:
        if self.node_selector == {"_PLACEHOLDER": "true"}:
            self.node_selector = {GENEVA_RAY_HEAD_NODE: ""}

    @property
    def _ports(self) -> list[dict]:
        return [
            {
                "containerPort": 10001,
                "name": "client",
                "protocol": "TCP",
            },
            {
                "containerPort": 8265,
                "name": "dashboard",
                "protocol": "TCP",
            },
            {
                "containerPort": 6379,
                "name": "gsc-server",
                "protocol": "TCP",
            },
        ]

    @property
    def definition(self) -> dict:
        definition = {
            "rayStartParams": {
                # do not schedule tasks onto the head node this prevents cluster
                # crashes due to other tasks killing the head node
                "num-cpus": "0"
            },
            "template": {
                "spec": {
                    **(self._priority_class or {}),
                    **(self._service_account or {}),
                    "containers": [
                        {
                            "name": "ray-head",
                            "image": self.image,
                            "imagePullPolicy": "IfNotPresent",
                            "resources": self._resources,
                            "ports": self._ports,
                            "volumeMounts": self.mounts_definition,
                        }
                    ],
                    "volumes": self.volume_definition,
                    "nodeSelector": self.node_selector,
                }
            },
        }

        return definition


@attrs.define(kw_only=True)
class _WorkerGroupSpec(_PodSpec):
    """
    A worker group specification for a Ray cluster.
    """

    name: str = attrs.field(default="worker")

    @name.validator
    def _validate_name(self, attribute: str, value: str) -> None:
        if not value:
            raise ValueError("name cannot be empty")

        if not re.match(r"^[a-zA-Z0-9\-]+$", value):
            raise ValueError(
                "name must only contain alphanumeric characters and dashes"
            )

    node_selector: dict[str, str] = attrs.field(default={"_PLACEHOLDER": "true"})

    replicas: int = attrs.field(
        default=1,
        validator=attrs.validators.ge(0),
    )

    idle_timeout_seconds: int = attrs.field(
        default=60,
        validator=attrs.validators.ge(0),
    )

    min_replicas: int = attrs.field(
        default=0,
        validator=attrs.validators.ge(0),
    )
    max_replicas: int = attrs.field(
        default=100,
    )

    @max_replicas.validator
    def _validate_max_replicas(self, attribute: str, value: int) -> None:
        if value == 0:
            raise ValueError("max_replicas must be greater than 0")

        if value < self.min_replicas:
            raise ValueError(
                f"max_replicas ({value}) must be greater than or",
                f" equal to min_replicas ({self.min_replicas})",
            )

    def __attrs_post_init__(self) -> None:
        if self.node_selector == {"_PLACEHOLDER": "true"}:
            if self.num_gpus > 0:
                # note: blank label values are not supported in EKS
                self.node_selector = {GENEVA_RAY_GPU_NODE: ""}
            else:
                self.node_selector = {GENEVA_RAY_CPU_NODE: ""}

    @property
    def _start_params(self) -> dict:
        params = {
            "num-cpus": str(self.num_cpus),
            "num-gpus": str(self.num_gpus),
        }

        # add a special resource for CPU only nodes
        # so that actors can be forced to run on CPU only nodes
        # in practice it looks like this
        # actor.options(num_cpus=1) can be scheduled on
        # * CPU only nodes, or
        # * GPU nodes with >= 1 CPU
        #
        # however, it is usually wasteful to schedule cpu-only actors
        # on GPU nodes. This allows us to force them to run on CPU only nodes
        if self.num_gpus == 0:
            # this param needs to be a JSON-string of a JSON-string
            # https://docs.ray.io/en/latest/ray-core/scheduling/resources.html#codecell3
            params["resources"] = json.dumps(json.dumps({CPU_ONLY_NODE: 10**5}))

        return params

    @property
    def definition(self) -> dict:
        return {
            "groupName": self.name,
            "replicas": self.replicas,
            "minReplicas": self.min_replicas,
            "maxReplicas": self.max_replicas,
            "idleTimeoutSeconds": self.idle_timeout_seconds,
            "rayStartParams": self._start_params,
            "template": {
                "spec": {
                    **(self._priority_class or {}),
                    **(self._service_account or {}),
                    "containers": [
                        {
                            "name": "ray-worker",
                            "image": self.image,
                            "imagePullPolicy": "IfNotPresent",
                            "resources": self._resources,
                            "volumeMounts": self.mounts_definition,
                            "env": [
                                {
                                    "name": "RAY_memory_usage_threshold",
                                    "value": "0.9",  # Adjust the threshold as needed
                                },
                                {
                                    "name": "RAY_memory_monitor_refresh_ms",
                                    "value": "0",  # Set to 0 disables the auto-kill
                                },
                            ],
                        }
                    ],
                    "volumes": self.volume_definition,
                    "nodeSelector": self.node_selector,
                }
            },
        }


class ExitMode(enum.Enum):
    """
    Behavior on context manager exit.
    DELETE will always delete the RayCluster on exit.
    DELETE_ON_SUCCESS will delete the RayCluster on success,
        but retain it if there is an error.
    RETAIN will always retain the RayCluster.
    """

    DELETE = "delete"
    DELETE_ON_SUCCESS = "delete_on_success"
    RETAIN = "retain"


@attrs.define(kw_only=True)
class RayCluster(_RayVersionMixin, _ValidationVisitable):
    """
    A Ray cluster specification.

    This is also a context manager for managing a Ray cluster.
    This context manager will apply the Ray cluster definition to the
    Kubernetes cluster when entering the context and delete the Ray
    cluster from the Kubernetes cluster when exiting the context.

    When entering the context, ray.init will be called with the address of the
    Ray cluster head node. When exiting the context, ray.shutdown will be
    called to shutdown the Ray cluster.

    Example:
        >>> from geneva.runners.ray.raycluster import RayCluster, cluster
        >>> head_group = _HeadGroupSpec(image="rayproject/ray:latest")
        >>> worker_group = _WorkerGroupSpec(name="worker", image="rayproject/ray")
        >>> with RayCluster(
        ...     name="test-cluster",
        ...     head_group=head_group,
        ...     worker_groups=[worker_group],
        ... ):
        ...     print("Ray cluster is running")
        Ray cluster is running
    """

    name: str = attrs.field()
    """
    The name of the Ray cluster. This name is used for deduplication of Ray
    clusters in the Kubernetes cluster. When a Ray cluster with the same name
    already exists, we will not create a new one.

    TODO: add a recreate=True option to force the recreation of the cluster.
    """

    @name.default
    def _default_name(self) -> str:
        config = _RayClusterConfig.get()
        return f"geneva-{config.user}"

    namespace: str = attrs.field()
    """
    The namespace of the Ray cluster. This is the namespace in which the Ray
    cluster will be created in the Kubernetes cluster.

    By default, we use `geneva` as the namespace.
    """

    @namespace.default
    def _default_namespace(self) -> str:
        config = _RayClusterConfig.get()
        return config.namespace

    head_group: _HeadGroupSpec = attrs.field(factory=_HeadGroupSpec)
    """
    The head group specification for the Ray cluster.
    """

    worker_groups: list[_WorkerGroupSpec] = attrs.field(
        factory=lambda: [_WorkerGroupSpec()]
    )
    """
    The worker group specifications for the Ray cluster.
    """

    strict_access_review: bool = attrs.field(
        default=False,
    )
    """
    Fail the access review for the service account if any errors occur.
    e.g. if we don't have permission to create local subject access reviews
    """

    config_method: K8sConfigMethod = attrs.field(default=K8sConfigMethod.LOCAL)
    """
    Method to retrieve kubeconfig
    """

    region: str = attrs.field(
        default=None,
    )
    """
    Optional cloud region where the cluster is located
    """

    cluster_name: str = attrs.field(
        default=None,
    )
    """
    Optional k8s cluster name, required for EKS auth
    """

    role_name: str = attrs.field(
        default=None,
    )
    """
    Optional IAM role name, required for EKS auth
    """

    on_exit: ExitMode = attrs.field(
        default=ExitMode.DELETE,
    )
    """
    Context manager behavior on exit. By default, the
    RayCluster will be deleted on exit.
    """

    @classmethod
    def from_config_map(
        cls,
        k8s_namespace: str,
        k8s_cluster_name: str,
        config_map_name: str,
        name: str,
        *,
        config_method: K8sConfigMethod = K8sConfigMethod.LOCAL,
        aws_region: str | None = None,
        aws_role_name: str | None = None,
    ) -> "RayCluster":
        """
        Create a RayCluster from an existing Kubernetes ConfigMap.

        Args:
            k8s_namespace: Namespace of the ConfigMap.
            k8s_cluster_name: Name of the Kubernetes cluster
            config_map_name: Name of the ConfigMap to load the RayCluster spec from.
            name: Name of the RayCluster to create
            config_method: Optional Method to retrieve kubeconfig.
            aws_region: Cloud region for EKS auth.
            aws_role_name: IAM role name for EKS auth.
        """
        api_client = build_api_client(
            config_method, aws_region, k8s_cluster_name, aws_role_name
        )
        core_api = kubernetes.client.CoreV1Api(api_client=api_client)
        cm = core_api.read_namespaced_config_map(
            name=config_map_name, namespace=k8s_namespace
        )
        data = cm.data or {}

        _LOG.debug(f"loaded config map {config_map_name}: {data}")

        config_kwargs: dict[str, Any] = {}
        for key, value in data.items():
            try:
                config_kwargs[key] = yaml.safe_load(value)
            except Exception:  # noqa: PERF203
                config_kwargs[key] = value

        try:
            config_kwargs["name"] = name
            config_kwargs["namespace"] = k8s_namespace
            config_kwargs["config_method"] = config_method
            config_kwargs["region"] = aws_region
            config_kwargs["role_name"] = aws_role_name
            config_kwargs["head_group"] = _HeadGroupSpec(
                **config_kwargs.get("head_group")
            )
            config_kwargs["worker_groups"] = [
                _WorkerGroupSpec(**w) for w in config_kwargs["worker_groups"]
            ]
            res = cls(**config_kwargs)
        except Exception as e:
            _LOG.error(f"error parsing ConfigMap data for {config_map_name}", e)
            raise Exception(
                f"unable to parse ConfigMap data for {config_map_name}: {str(e)}"
            ) from e

        return res

    def to_config_map(self) -> dict[str, str]:
        """
        Serialize this RayCluster into a dict of YAML strings suitable for
        storing in a Kubernetes ConfigMap.data field.
        Keys include 'name', 'head_group', and 'worker_groups'.
        """
        data: dict[str, str] = {}
        data["name"] = self.name
        head_dict = attrs.asdict(self.head_group)
        # remove internal attrs
        for key in ("ray_version", "python_version"):
            head_dict.pop(key, None)
        data["head_group"] = yaml.safe_dump(head_dict, sort_keys=False)
        wgs: list[dict[str, Any]] = []
        for w in self.worker_groups:
            wd = attrs.asdict(w)
            for key in ("ray_version", "python_version"):
                wd.pop(key, None)
            wgs.append(wd)
        data["worker_groups"] = yaml.safe_dump(wgs, sort_keys=False)
        return data

    def __attrs_post_init__(self) -> None:
        # Initialize CustomObjectsApi client based on config_method
        client = build_api_client(
            self.config_method, self.region, self.cluster_name, self.role_name
        )
        self.custom_api = kubernetes.client.CustomObjectsApi(api_client=client)
        self.core_api = kubernetes.client.CoreV1Api(api_client=client)
        self.auth_api = kubernetes.client.AuthorizationV1Api(api_client=client)
        self.scheduling_api = scheduling_v1_api.SchedulingV1Api(api_client=client)

    @property
    def _autoscaler_options(self) -> dict:
        """
        The autoscaler options for the Ray cluster.
        """
        # TODO: allow customization of the autoscaler options
        return {
            "version": "v2",
            "enableInTreeAutoscaling": True,
            "env": [{"name": "RAY_enable_autoscaler_v2", "value": "1"}],
            "envFrom": [],
            "idleTimeoutSeconds": 60,
            "imagePullPolicy": "IfNotPresent",
            "resources": {
                "requests": {
                    "cpu": "1",
                    "memory": "1Gi",
                },
                "limits": {
                    "cpu": "1",
                    "memory": "1Gi",
                },
            },
            "upscalingMode": "Default",
        }

    @property
    def spec(self) -> dict:
        """
        The Ray cluster specification.

        This can be used as part of RayJob for configuring the Ray cluster.
        """
        return {
            "enableInTreeAutoscaling": True,
            "autoscalerOptions": self._autoscaler_options,
            "rayVersion": self.ray_version,
            "headGroupSpec": self.head_group.definition,
            "workerGroupSpecs": [worker.definition for worker in self.worker_groups],
        }

    @property
    def definition(self) -> dict:
        """
        The Ray cluster definition.

        This is the full definition of the Ray cluster, including the name and
        autoscaler options. This can be used to create the Ray cluster in the
        Kubernetes cluster via a CRD.
        """
        return {
            "apiVersion": "ray.io/v1",
            "kind": "RayCluster",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
            },
            "spec": self.spec,
        }

    def _has_existing_cluster(self) -> bool:
        try:
            self.custom_api.get_namespaced_custom_object(
                group="ray.io",
                version="v1",
                namespace=self.namespace,
                plural="rayclusters",
                name=self.name,
            )
        except kubernetes.client.exceptions.ApiException as e:
            if e.status == 404:
                return False
            raise e
        return True

    def _wait_for_cluster(self) -> Any:
        while True:
            # TODO: add wait for the Ray cluster to be ready
            # TODO: add timeout
            result = self.custom_api.get_namespaced_custom_object(
                group="ray.io",
                version="v1",
                namespace=self.namespace,
                plural="rayclusters",
                name=self.name,
            )
            assert isinstance(result, dict)

            if "status" not in result:
                _LOG.debug("Waiting for the Ray cluster to be ready")
                time.sleep(1)
                continue

            status = result["status"]
            assert isinstance(status, dict)

            if "head" not in status:
                _LOG.debug("Waiting for the head node to be ready")
                time.sleep(1)
                continue

            head = status["head"]
            assert isinstance(head, dict)

            if "podIP" not in head:
                _LOG.debug("Waiting for the head node IP address")
                time.sleep(1)
                continue

            _LOG.debug("Ray cluster is ready")
            return result

    def _wait_for_head_node(self, pod_name: str) -> Any:
        while True:
            pod = self.core_api.read_namespaced_pod(
                name=pod_name, namespace=self.namespace
            )
            if pod.status.phase != "Running":
                _LOG.debug("Waiting for the head node to be running")
                time.sleep(1)
                continue

            _LOG.debug("Head node is running")
            return pod

    def _get_podname(
        self,
    ) -> str:  # why is api paratemterize here?
        cluster = self._wait_for_cluster()
        _LOG.info(f"cluster status: {cluster['status']}")

        # kuberay 1.2+
        pod_name = cluster.get("status", {}).get("head", {}).get("podName")
        if pod_name:
            return pod_name

        # kuberay 1.1 version.
        label_selector = f"ray.io/cluster={self.name},ray.io/node-type=head"
        pods = self.core_api.list_namespaced_pod(
            namespace=self.namespace,
            label_selector=label_selector,
        )

        for pod in pods.items:
            if pod.status.phase == "Running":
                return pod.metadata.name
        raise RuntimeError(f"Failed to find head node pod for cluster {self.name}")

    @property
    def head_node_pod(self) -> Any:
        self._wait_for_cluster()
        pod_name = self._get_podname()
        return self._wait_for_head_node(pod_name)

    def _expose_node_port(self) -> None:
        _LOG.info("Exposing head node on a node port")
        # create a service to expose the head node
        self.core_api.create_namespaced_service(
            namespace=self.namespace,
            body={
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": f"{self.name}-head",
                    "namespace": self.namespace,
                },
                "spec": {
                    "ports": [
                        {
                            "name": "client",
                            "port": 10001,
                            "nodePort": 30001,
                        },
                    ],
                    "selector": {
                        "ray.io/identifier": f"{self.name}-head",
                    },
                    "type": "NodePort",
                },
            },
        )

    def apply(self) -> str:
        """
        Apply the Ray cluster definition to the Kubernetes cluster.

        returns the ip address of the head node
        """
        self._validate()

        if self._has_existing_cluster():
            _LOG.info(
                "Ray cluster already exists, patching instead of creating a new one."
                " This means existing nodes will not update until they are recreated."
                " Use recreate=True to force recreation."
            )
            self.custom_api.patch_namespaced_custom_object(
                group="ray.io",
                version="v1",
                namespace=self.namespace,
                plural="rayclusters",
                name=self.name,
                body=self.definition,
            )
        else:
            self.custom_api.create_namespaced_custom_object(
                group="ray.io",
                version="v1",
                namespace=self.namespace,
                plural="rayclusters",
                body=self.definition,
            )

        try:
            pod = self.head_node_pod

            return pod.status.pod_ip
        except Exception:
            _LOG.warning("Falling back to kuberay 1.1 cluster status")
            # kuberay 1.1 version of cluster['status'].  kuberay 1.2+ has
            # cluster['status']['head']['podName'] which is used to look up
            # the head node's ip
            """
            {
                ...
                "head": {"podIP": "10.104.5.6", "serviceIP": "34.118.237.31"},
                ...
                "state": "ready",
            }
            """
            while True:
                cluster = self._wait_for_cluster()
                _LOG.info(f"cluster status waiting for head: {cluster['status']}")
                head_ip = cluster["status"]["head"].get("podIP")
                if head_ip is None:
                    _LOG.info(
                        "waiting for kuberay 1.1 head node to be ready but"
                        f" no IP: {head_ip}"
                    )
                    time.sleep(1)
                    cluster = self._wait_for_cluster()
                    continue
                _LOG.info(f"kuberay 1.1 head node is running @ {head_ip}")
                return head_ip

    def delete(self) -> None:
        """
        Delete the Ray cluster from the Kubernetes cluster.
        """
        try:
            if not ray.is_initialized():
                # skip if ray is not initilized
                _LOG.warning("Ray was not initialized")

            if not self._has_existing_cluster():
                _LOG.warning("No kuberay cluster to shutdown")
                return
            self.custom_api.delete_namespaced_custom_object(
                group="ray.io",
                version="v1",
                namespace=self.namespace,
                plural="rayclusters",
                name=self.name,
            )
        except kubernetes.client.exceptions.ApiException as e:
            if e.status == 404:
                _LOG.info("Ray cluster does not exist, nothing to delete")
                return
            _LOG.exception("Failed to delete Ray cluster")
            raise e
        except Exception as e:
            _LOG.exception("Failed to delete Ray cluster")
            raise e

    def __enter__(self) -> str:
        _LOG.info("Starting Ray cluster")
        return self.apply()

    def __exit__(self, exc_type=None, exc_value=None, traceback=None) -> None:
        success = exc_type is None

        if self.on_exit == ExitMode.DELETE:
            self.delete()
        elif self.on_exit == ExitMode.DELETE_ON_SUCCESS:
            if success:
                self.delete()
            else:
                _LOG.info("retaining RayCluster due to error")
        elif self.on_exit == ExitMode.RETAIN:
            _LOG.info("retaining RayCluster due to ExitMode.RETAIN")
        else:
            raise Exception(f"unsupported exit_mode: {self.on_exit}")

    def _validate(self, visitor=None) -> None:
        if visitor is None:
            visitor = _ValidationVisitor()
        with (
            visitor.with_namespace(self.namespace),
            visitor.with_cluster_name(self.name),
            visitor.with_strict_access_review(self.strict_access_review),
            visitor.with_core_api(self.core_api),
            visitor.with_auth_api(self.auth_api),
            visitor.with_scheduling_api(self.scheduling_api),
        ):
            self.head_group._validate(visitor)
            for worker in self.worker_groups:
                worker._validate(visitor)


def _can_i(
    *,
    auth_api: kubernetes.client.AuthorizationV1Api,
    namespace: str,
    sa: str,
    verb: str,
    resource: str,
    name: str,
    group: str | None = None,
) -> bool:
    """
    Check if the service account has permission to perform the action
    """
    res = auth_api.create_namespaced_local_subject_access_review(
        namespace=namespace,
        body={
            "apiVersion": "authorization.k8s.io/v1",
            "kind": "LocalSubjectAccessReview",
            "spec": {
                "user": f"system:serviceaccount:{namespace}:{sa}",
                "resourceAttributes": {
                    "namespace": namespace,
                    "verb": verb,
                    "resource": resource,
                    "name": name,
                    **({"group": group} if group else {}),
                },
            },
        },
    )

    return res.status.allowed


@attrs.define
class _ValidationVisitor:
    cluster_name: str | None = attrs.field(init=False, default=None)
    namespace: str | None = attrs.field(init=False, default=None)
    strict_access_review: bool = attrs.field(init=False, default=False)
    core_api: kubernetes.client.CoreV1Api = attrs.field(init=False, default=False)
    auth_api: kubernetes.client.AuthorizationV1Api = attrs.field(
        init=False, default=False
    )
    scheduling_api: scheduling_v1_api.SchedulingV1Api = attrs.field(
        init=False, default=False
    )

    @contextlib.contextmanager
    def with_namespace(self, namespace: str) -> Generator[None, None, None]:
        old = self.namespace
        self.namespace = namespace
        yield
        self.namespace = old

    @contextlib.contextmanager
    def with_cluster_name(self, cluster_name: str) -> Generator[None, None, None]:
        old = self.cluster_name
        self.cluster_name = cluster_name
        yield
        self.cluster_name = old

    @contextlib.contextmanager
    def with_strict_access_review(self, value: bool) -> Generator[None, None, None]:
        old = self.strict_access_review
        self.strict_access_review = value
        yield
        self.strict_access_review = old

    @contextlib.contextmanager
    def with_core_api(self, value) -> Generator[None, None, None]:
        old = self.core_api
        self.core_api = value
        yield
        self.core_api = old

    @contextlib.contextmanager
    def with_auth_api(self, value) -> Generator[None, None, None]:
        old = self.auth_api
        self.auth_api = value
        yield
        self.auth_api = old

    @contextlib.contextmanager
    def with_scheduling_api(self, value) -> Generator[None, None, None]:
        old = self.scheduling_api
        self.scheduling_api = value
        yield
        self.scheduling_api = old

    def _check_sa_access(self, sa: _ServiceAccountMixin) -> None:
        # list all the role bindings on the service account
        # and check we have the correct permissions
        permissions_needed = [
            {
                "verb": "get",
                "resource": "pods",
                "name": "*",
            },
            {
                "verb": "list",
                "resource": "pods",
                "name": "*",
            },
            {
                "verb": "watch",
                "resource": "pods",
                "name": "*",
            },
            {
                "verb": "get",
                "resource": "rayclusters",
                "name": self.cluster_name,
                "group": "ray.io",
            },
            {
                "verb": "patch",
                "resource": "rayclusters",
                "name": self.cluster_name,
                "group": "ray.io",
            },
        ]
        checker = functools.partial(
            _can_i,
            auth_api=self.auth_api,
            namespace=self.namespace,
            sa=sa.service_account,
        )
        passed = True
        error_str = ""
        for perm in permissions_needed:
            if not checker(**perm):
                error_str += (
                    f"Service account {sa.service_account} does not have the "
                    f"required permission: {perm['verb']} {perm['resource']}"
                )
                passed = False
        if not passed:
            raise ValueError(error_str)

    def visit_service_account(self, sa: _ServiceAccountMixin) -> None:
        if sa.service_account is None:
            return

        # validate the service account exists
        try:
            service_account = self.core_api.read_namespaced_service_account(
                name=sa.service_account, namespace=self.namespace
            )
        except kubernetes.client.exceptions.ApiException as e:
            if e.status == 404:
                raise ValueError(
                    f"Service account {sa.service_account} does not exist"
                ) from e
            raise e

        try:
            self._check_sa_access(sa)
        except ValueError:
            raise
        except Exception:
            if self.strict_access_review:
                raise
            _LOG.exception(
                "Skipping access review for service account %s due to exception",
                sa.service_account,
            )

        if service_account.metadata.annotations is None:
            raise ValueError(
                f"Service account {sa.service_account} does not have any annotations"
            )

        # TODO: need different modes of permission check here
        if (
            "iam.gke.io/gcp-service-account" not in service_account.metadata.annotations
            and "eks.amazonaws.com/role-arn" not in service_account.metadata.annotations
        ):
            raise ValueError(
                f"Service account {sa.service_account} does not have a "
                f"cloud service account or role"
            )

    def visit_priority_class(self, pri: _PriorityClassMixin) -> None:
        if pri.priority_class is None:
            return

        # validate the priority class exists
        try:
            self.scheduling_api.read_priority_class(name=pri.priority_class)
        except kubernetes.client.exceptions.ApiException as e:
            if e.status == 404:
                raise ValueError(
                    f"Priority class {pri.priority_class} does not exist"
                ) from e
            raise e

    def visit_image(self, img: _ImageMixin) -> None:
        local_arch = platform.processor()

        # note: 1) this may not work for custom Ray images.
        # 2) Ray multi-platform images do not contain the arch suffix, but we don't
        # need to warn in that case
        is_img_arm = "aarch64" in img.image
        is_local_arm = local_arch in {"aarch64", "arm"}

        # log a warning if the image architecture differs from the
        # local CPU architecture
        if is_img_arm != is_local_arm:
            _LOG.warning(
                f"Ray image architecture does not match current architecture. "
                f"This may result in dependency errors on workers. Please ensure "
                f"worker nodes are using the same CPU architecture as the Geneva "
                f"client. Ray image: {img.image} Current architecture: {local_arch}"
            )

    def visit_head_node(self, _: _HeadGroupSpec) -> None:
        pass

    def visit_worker_node(self, _: _WorkerGroupSpec) -> None:
        pass


T = TypeVar("T")


def ray_tqdm(iterable: Iterable[T], job_tracker, metric: str) -> Iterator[T]:
    for item in iterable:
        job_tracker.increment.remote(metric, 1)
        yield item
    job_tracker.mark_done.remote(metric)


@attrs.define
class ClusterStatus:
    pbar_k8s = attrs.field(default=None)
    pbar_pods = attrs.field(default=None)

    last_cnt_k8s = attrs.field(default=0)
    last_cnt_pods = attrs.field(default=0)

    def get_status(self) -> None:
        try:
            k8s_status = _k8s_status()
            pods_running = [i[0] for i in k8s_status if i[1] == "Running"]
            if self.pbar_k8s is None:
                fmt = "{l_bar}{bar} {n_fmt} [{elapsed}]"
                self.pbar_k8s = tqdm(desc="Cluster nodes provisioned", bar_format=fmt)
            self.pbar_k8s.update(len(pods_running) - self.last_cnt_k8s)
            self.last_cnt_k8s = len(pods_running)
        except Exception:
            _LOG.info("failed to get k8s node status")
            # do nothing

        try:
            ray_status = _ray_status()
            cnt_workers = ray_status.get("ray_nodes", 0)
            if self.pbar_pods is None:
                fmt = "{l_bar}{bar} {n_fmt} [{elapsed}]"
                self.pbar_pods = tqdm(desc="Workers scheduled", bar_format=fmt)
            self.pbar_pods.update(cnt_workers - self.last_cnt_pods)
            self.last_cnt_pods = cnt_workers
        except Exception:
            _LOG.info("failed to get ray status")
            # do nothing

    def close(self) -> None:
        self.pbar_k8s.close()
        self.pbar_pods.close()
