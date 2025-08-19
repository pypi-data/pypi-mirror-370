# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import importlib
import logging
import subprocess
from contextlib import suppress

import pytest
import ray
import ray.exceptions

from geneva.eks import K8sConfigMethod
from geneva.runners.ray._mgr import ray_cluster
from geneva.runners.ray.raycluster import (
    CPU_ONLY_NODE,
    RayCluster,
    _HeadGroupSpec,
    _WorkerGroupSpec,
)
from geneva.utils import dt_now_utc

logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)


def test_cluster_startup(
    k8s_config_method: K8sConfigMethod,
    head_node_selector: dict,
    worker_node_selector: dict,
    slug: str | None,
) -> None:
    cluster_name = "geneva-integ-test"
    cluster_name += f"-{dt_now_utc().strftime('%Y-%m-%d-%H-%M')}-{slug}"

    with ray_cluster(
        name=cluster_name,
        namespace="geneva",
        config_method=k8s_config_method,
        head_group=_HeadGroupSpec(node_selector=head_node_selector),
        # allocate at least a single worker so the test runs faster
        # that we save time on waiting for the actor to start
        worker_groups=[
            _WorkerGroupSpec(
                name="worker",
                min_replicas=1,
                node_selector=worker_node_selector,
            )
        ],
        use_portforwarding=True,
    ):
        ray.get(ray.remote(lambda: 1).remote())


def test_cluster_startup_config_map(
    cluster_from_config_map: RayCluster,
    slug: str | None,
) -> None:
    cluster_name = "geneva-integ-test"
    cluster_name += f"-{dt_now_utc().strftime('%Y-%m-%d-%H-%M')}-{slug}"

    with ray_cluster(ray_cluster=cluster_from_config_map):
        res = ray.get(ray.remote(lambda: __import__("sys").version).remote())
        _LOG.info(f"***done {res=}")


def test_cluster_startup_no_account(
    k8s_config_method: K8sConfigMethod,
    head_node_selector: dict,
    worker_node_selector: dict,
    slug: str | None,
) -> None:
    """
    Test the if we try to import geneva, which uses gcs for
    workspace packaging magic, errors when the service account
    doesn't have permission to access the gcs bucket.
    """

    cluster_name = "geneva-integ-test"
    cluster_name += f"-{dt_now_utc().strftime('%Y-%m-%d-%H-%M')}-{slug}"

    with (
        pytest.raises(ValueError, match=r"Service account .* does not exist"),
        ray_cluster(
            name=cluster_name,
            namespace="geneva",
            config_method=k8s_config_method,
            use_portforwarding=True,
            head_group=_HeadGroupSpec(node_selector=head_node_selector),
            # allocate at least a single worker so the test runs faster
            # that we save time on waiting for the actor to start
            worker_groups=[
                _WorkerGroupSpec(
                    name="worker",
                    min_replicas=1,
                    service_account="bogus-service-account",
                    node_selector=worker_node_selector,
                )
            ],
        ),
    ):
        ray.get(ray.remote(lambda: importlib.import_module("geneva")).remote())


@pytest.mark.skip("Need to create a service account with no permissions")
def test_cluster_startup_no_gcs_permission(
    k8s_config_method: K8sConfigMethod,
    head_node_selector: dict,
    worker_node_selector: dict,
    slug: str | None,
) -> None:
    """
    Test the if we try to import geneva, which uses gcs for
    workspace packaging magic, errors when the service account
    doesn't have permission to access the gcs bucket.
    """

    cluster_name = "geneva-integ-test"
    cluster_name += f"-{dt_now_utc().strftime('%Y-%m-%d-%H-%M')}-{slug}"

    with (
        ray_cluster(
            name=cluster_name,
            namespace="geneva",
            config_method=k8s_config_method,
            use_portforwarding=True,
            # allocate at least a single worker so the test runs faster
            # that we save time on waiting for the actor to start
            head_group=_HeadGroupSpec(node_selector=head_node_selector),
            worker_groups=[
                _WorkerGroupSpec(
                    name="worker",
                    min_replicas=1,
                    service_account="valid-no-perms-service-account",
                    node_selector=worker_node_selector,
                )
            ],
        ),
        pytest.raises(PermissionError, match="PERMISSION_DENIED"),
    ):
        ray.get(ray.remote(lambda: importlib.import_module("geneva")).remote())


def test_cluster_startup_can_import_geneva_and_lance(
    geneva_k8s_service_account: str,
    k8s_config_method: K8sConfigMethod,
    head_node_selector: dict,
    worker_node_selector: dict,
    slug: str | None,
) -> None:
    """
    Test the if we try to import geneva, which uses gcs for
    workspace packaging magic, errors when the service account
    doesn't have permission to access the gcs bucket.
    """

    cluster_name = "geneva-integ-test"
    cluster_name += f"-{dt_now_utc().strftime('%Y-%m-%d-%H-%M')}-{slug}"

    with ray_cluster(
        name=cluster_name,
        namespace="geneva",
        config_method=k8s_config_method,
        use_portforwarding=True,
        head_group=_HeadGroupSpec(
            service_account=geneva_k8s_service_account,
            node_selector=head_node_selector,
        ),
        # allocate at least a single worker so the test runs faster
        # that we save time on waiting for the actor to start
        worker_groups=[
            _WorkerGroupSpec(
                name="worker",
                min_replicas=1,
                service_account=geneva_k8s_service_account,
                node_selector=worker_node_selector,
            )
        ],
    ):
        ray.get(ray.remote(lambda: importlib.import_module("geneva")).remote())
        ray.get(ray.remote(lambda: importlib.import_module("lance")).remote())


def test_cluster_startup_skip_site(
    geneva_k8s_service_account: str,
    k8s_config_method: K8sConfigMethod,
    head_node_selector: dict,
    worker_node_selector: dict,
    slug: str | None,
) -> None:
    """
    Test that if we try to import geneva, which uses gcs for
    workspace packaging magic, errors because we skipped site
    packages and can't find
    """

    cluster_name = "geneva-integ-test"
    cluster_name += f"-{dt_now_utc().strftime('%Y-%m-%d-%H-%M')}-{slug}"

    with (
        ray_cluster(
            name=cluster_name,
            namespace="geneva",
            config_method=k8s_config_method,
            use_portforwarding=True,
            head_group=_HeadGroupSpec(
                service_account=geneva_k8s_service_account,
                node_selector=head_node_selector,
            ),
            # allocate at least a single worker so the test runs faster
            # that we save time on waiting for the actor to start
            worker_groups=[
                _WorkerGroupSpec(
                    name="worker",
                    min_replicas=1,
                    service_account=geneva_k8s_service_account,
                    node_selector=worker_node_selector,
                )
            ],
            skip_site_packages=True,
        ),
        pytest.raises(ImportError, match=r"^(?!.*(geneva)).+"),
    ):
        # match the word geneva is not in the error message
        # so we know that geneva is uploaded but not lance, which
        # is expected because we skipped site packages
        ray.get(ray.remote(lambda: importlib.import_module("geneva")).remote())


def test_cluster_startup_cpu_only_tag(
    geneva_k8s_service_account: str,
    k8s_config_method: K8sConfigMethod,
    head_node_selector: dict,
    worker_node_selector: dict,
    csp: str,
    slug: str | None,
) -> None:
    """
    Test that if we force a CPU only task, it runs only on a CPU worker.

    If we request a GPU worker, it can run GPU worker, if we don't request a GPU worker
    without the cpu-only tag, it can be scheduled to runs on either a CPU or GPU worker.

    Oftentimes GPU workers fail to provision so we let the test pass in this case.
    """

    cluster_name = "geneva-integ-test"
    cluster_name += f"-{dt_now_utc().strftime('%Y-%m-%d-%H-%M')}-{slug}"

    try:
        with ray_cluster(
            name=cluster_name,
            namespace="geneva",
            config_method=k8s_config_method,
            use_portforwarding=True,
            head_group=_HeadGroupSpec(
                service_account=geneva_k8s_service_account,
                node_selector=head_node_selector,
            ),
            # allocate both GPU and CPU workers
            worker_groups=[
                _WorkerGroupSpec(
                    name="cpu",
                    min_replicas=0,
                    service_account=geneva_k8s_service_account,
                    num_cpus=2,
                    node_selector=worker_node_selector,
                ),
                _WorkerGroupSpec(
                    name="gpu",
                    min_replicas=1,
                    service_account=geneva_k8s_service_account,
                    num_gpus=1,
                    num_cpus=2,
                    node_selector={"geneva.lancedb.com/ray-worker-gpu": "true"}
                    if csp == "aws"
                    else {"_PLACEHOLDER": "true"},
                ),
            ],
        ):
            ray.get(
                ray.remote(num_gpus=1)(
                    lambda: subprocess.run("nvidia-smi", check=True)
                ).remote()
            )
            # running a CPU only task but we have a GPU worker
            # should schedule on the GPU worker but may schedule on CPU
            with suppress(ray.exceptions.RayTaskError):
                ray.get(
                    ray.remote(
                        lambda: subprocess.run("nvidia-smi", check=True)
                    ).remote()
                )

            # running a CPU only task + force it to run on CPU
            # should only schedule on the CPU worker and should always raise exception
            with pytest.raises(
                ray.exceptions.RayTaskError,
                match="No such file or directory: 'nvidia-smi'",
            ):
                ray.get(
                    ray.remote(resources={CPU_ONLY_NODE: 1})(
                        lambda: subprocess.run("nvidia-smi", check=True)
                    ).remote()
                )
    except (ConnectionError, RuntimeError):
        pytest.skip(
            "Skipping test due to Ray cluster startup failure "
            "(likely cannot provision GPU node): {e}"
        )
