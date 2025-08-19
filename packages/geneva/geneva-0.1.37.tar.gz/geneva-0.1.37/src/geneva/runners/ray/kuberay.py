import hashlib
import json
import logging
import random

import attrs
import ray
from kubernetes import client
from kubernetes import config as kube_config

from geneva.config import ConfigBase
from geneva.eks import _KUBE_API_CLIENT

_LOG = logging.getLogger(__name__)

KUBERAY_API_GROUP = "ray.io"  # API group for KubeRay RayCluster CRD
KUBERAY_API_VERSION = "v1"  # CRD version
KUBERAY_API_GROUP_VERSION = f"{KUBERAY_API_GROUP}/{KUBERAY_API_VERSION}"
KUBERAY_JOB_API_KIND = "RayJob"
KUBERAY_JOB_API_NAME = "rayjobs"
KUBERAY_CLUSTER_PLURAL = "rayclusters"  # lowercase, plural form of the kind
GENEVA_NAMESPACE = "geneva"  # namespace where your clusters live


@attrs.define
class KuberayConfig(ConfigBase):
    checkpoint_store: str = attrs.field()
    ray_version: str = attrs.field()
    namespace: str = attrs.field(default="lancedb")
    worker_min_replicas: int = attrs.field(default=0)
    worker_max_replicas: int = attrs.field(default=10)

    @classmethod
    def name(cls) -> str:
        return "kuberay"


def launch_kuberay_job(
    db_uri: str,
    table_name: str,
    column: str,
    image: str,
    kuberay_config: KuberayConfig,
) -> None:
    # TODO api docs explaining the args supposed to be passed
    try:
        kube_config.load_kube_config()
    except Exception:
        kube_config.load_incluster_config()

    # note: this depends on prior call to build_api_client
    # and might be subject to race conditions
    api = client.CustomObjectsApi(api_client=_KUBE_API_CLIENT)

    job_definition = {
        "apiVersion": KUBERAY_API_GROUP_VERSION,
        "kind": KUBERAY_JOB_API_KIND,
        "metadata": {
            "name": generate_job_name(db_uri, table_name, column),
            "namespace": kuberay_config.namespace,
        },
        "spec": {
            "entrypoint": f"python3 -m geneva.runners.ray --db_uri {db_uri} --table_name {table_name} --column {column} --checkpoint_store {kuberay_config.checkpoint_store}",  # noqa E501
            "rayClusterSpec": {
                "rayVersion": kuberay_config.namespace,
                "headGroupSpec": {
                    "rayStartParams": {},
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "name": "ray-head",
                                    "image": image,
                                    "imagePullPolicy": "IfNotPresent",
                                    "ports": [
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
                                    ],
                                }
                            ]
                        }
                    },
                },
                "workerGroupSpecs": [
                    {
                        "groupName": "worker-group-1",
                        "minReplicas": kuberay_config.worker_min_replicas,
                        "maxReplicas": kuberay_config.worker_max_replicas,
                        "rayStartParams": {},
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "name": "ray-worker",
                                        "image": image,
                                        "imagePullPolicy": "IfNotPresent",
                                    }
                                ]
                            }
                        },
                    }
                ],
            },
        },
    }

    api.create_namespaced_custom_object(
        group=KUBERAY_API_GROUP,
        version=KUBERAY_API_VERSION,
        namespace=kuberay_config.namespace,
        plural=KUBERAY_JOB_API_NAME,
        body=job_definition,
    )


def generate_job_name(
    db_uri: str,
    table_name: str,
    column: str,
) -> str:
    db_name = db_uri.split("/")[-1]
    seed = random.randint(0, 1000000)
    job_name = f"ray-geneva-{db_name[:6]}-{table_name[6]}-{column[:6]}-{hashlib.md5(str(seed).encode()).hexdigest()[:6]}"  # noqa E501
    return job_name


def _ray_status() -> dict[str, any]:
    """Check the status of the compute cluster
    Checks ray actors, ray and k8s to show progress
    """
    status: dict[str, any] = {"ray_nodes": 0}
    try:
        rcr = ray.cluster_resources()
        _LOG.debug(f"ray cluster_resources: {rcr}")
    except Exception as e:
        _LOG.warning("geneva compute context not ready")
        status["error"] = e
        return status

    try:
        # of machines in ray cluster
        nodes = ray.nodes()
        live_nodes = [n for n in nodes if n["Alive"]]
        status["ray_nodes"] = len(live_nodes)
    except Exception as e:
        _LOG.exception("Problem listing ray nodes")
        status["error"] = e

    return status


def _ray_job_status() -> dict[str, any]:
    status: dict[str, any] = {"ray_actors": 0}
    try:
        # this requires connecting to the ray dashboard
        from ray.util.state import list_actors

        actors = list_actors()
        live_actors = [a for a in actors if a.state == "ALIVE"]
        live_applier_actors = [
            a.actor_id for a in live_actors if a.class_name == "ApplierActor"
        ]

        status["ray_applier_actors"] = len(live_applier_actors)
        status["ray_actors"] = len(live_actors)
        _LOG.debug(f"cluster status: {status}")
    except Exception as e:
        _LOG.exception("Problem listing actors")
        status["error"] = e
    return status


def _k8s_status(namespace: str = "geneva") -> list[any]:
    # global _KUBE_API_CLIENT
    # Load your kubeconfig (or in-cluster config if running inside Kubernetes)
    try:
        kube_config.load_kube_config()
    except Exception:
        kube_config.load_incluster_config()

    # Instantiate CoreV1Api (ignore custom api_client if None)
    core_api = client.CoreV1Api(api_client=_KUBE_API_CLIENT)

    # List all pods in the namespace
    pods = core_api.list_namespaced_pod(namespace)

    # Filter Ray pods by label (adjust depending on your RayCluster setup)
    ray_pods = [pod for pod in pods.items if "ray.io/node-type" in pod.metadata.labels]

    # Summarize pod phases and conditions
    detailed_status = []

    for pod in ray_pods:
        phase = pod.status.phase  # Pending, Running, Succeeded, Failed
        name = pod.metadata.name
        detailed_status.append((name, phase, pod.status.conditions))

    return detailed_status


def _k8s_cluster_status() -> dict[str, any]:
    kuberay_status = {}
    try:
        kube_config.load_kube_config()
    except Exception:
        kube_config.load_incluster_config()

    api = client.CustomObjectsApi(api_client=_KUBE_API_CLIENT)

    # List all RayClusters in the namespace
    clusters = api.list_namespaced_custom_object(
        group=KUBERAY_API_GROUP,
        version=KUBERAY_API_VERSION,
        namespace=GENEVA_NAMESPACE,
        plural=KUBERAY_CLUSTER_PLURAL,
    )

    for item in clusters.get("items", []):
        name = item["metadata"]["name"]
        status = item.get("status", {})
        cluster_status = {}

        _LOG.info(f"\nCluster: {name}")
        _LOG.info(f" status: {json.dumps(status, indent=2)}")
        # Newer KubeRay versions surface detailed pod/ready conditions:
        conditions = status.get("conditions", [])
        if conditions:
            for cond in conditions:
                t = cond.get("type")
                s = cond.get("status")
                m = cond.get("message", "").strip()
                _LOG.info(f"  Condition {t}: {s} — {m}")
        else:
            # Fallback: head/worker counts in status fields
            cluster_status["availableWorkerReplicas"] = status.get(
                "availableWorkerReplicas"
            )
            cluster_status["readyWorkerReplicas"] = status.get("readyWorkerReplicas")
            for wg in status.get("workerGroupStatuses", []):
                grp = wg.get("groupName")
                repl = wg.get("replicas")
                _LOG.info(f"  Worker group '{grp}' replicas ready: {repl}")
        kuberay_status[name] = cluster_status
    return kuberay_status
