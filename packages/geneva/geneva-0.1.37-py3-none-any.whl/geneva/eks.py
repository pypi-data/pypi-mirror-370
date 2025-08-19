# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import base64
import logging
import tempfile
from enum import Enum

from kubernetes import client, config

_LOG = logging.getLogger(__name__)

# Store a global singleton API client to reduce calls to STS/EKS
_KUBE_API_CLIENT: client.ApiClient | None = None


class K8sConfigMethod(Enum):
    EKS_AUTH = 1
    IN_CLUSTER = 2
    LOCAL = 3


def build_api_client(
    config_method: K8sConfigMethod,
    region: str | None = "us-east-1",
    cluster_name: str = "lancedb",
    role_name: str = "geneva-client-role",
) -> client.ApiClient | None:
    """Build the k8s API client based on the configuration method and region.
    The client is cached in a global variable to minimize expensive EKS calls.
    Returns None for default config method (non-EKS).
    """
    global _KUBE_API_CLIENT

    # Return cached client if available
    if _KUBE_API_CLIENT is not None:
        return _KUBE_API_CLIENT

    if config_method == K8sConfigMethod.IN_CLUSTER:
        config.load_incluster_config()

        return None
    elif config_method == K8sConfigMethod.LOCAL:
        config.load_kube_config()

        return None
    elif config_method == K8sConfigMethod.EKS_AUTH:
        ca_data, endpoint, token = _eks_auth(cluster_name, region, role_name)
        cafile = _write_cafile(ca_data)
        _KUBE_API_CLIENT = _api_client(endpoint, token, cafile.name)
        return _KUBE_API_CLIENT
    else:
        raise Exception(f"unsupported config method: {config_method}")


def _eks_auth(cluster_name: str, region: str, role_name: str) -> (str, str, str):
    import boto3
    import eks_token

    eks_client = boto3.client("eks", region_name=region)
    identity = boto3.client("sts", region_name=region).get_caller_identity()
    _LOG.debug("caller identity: %s", identity)
    acct_id = identity.get("Account")
    # this role requires an EKS Access Entry with
    # AmazonEKSClusterAdminPolicy on the given namespace
    # and must be assumable by the current user
    role_arn = f"arn:aws:iam::{acct_id}:role/{role_name}"
    token = eks_token.get_token(cluster_name, role_arn)["status"]["token"]
    cluster_data = eks_client.describe_cluster(name=cluster_name)["cluster"]
    ca_data = cluster_data["certificateAuthority"]["data"]
    endpoint = cluster_data["endpoint"]
    _LOG.info(f"authenticated with EKS. {cluster_name=} {role_arn=}")
    return ca_data, endpoint, token


def _write_cafile(data: str) -> tempfile.NamedTemporaryFile:
    # ruff: noqa: SIM115
    cafile = tempfile.NamedTemporaryFile(delete=False)
    cadata_b64 = data
    cadata = base64.b64decode(cadata_b64)
    cafile.write(cadata)
    cafile.flush()
    return cafile


def _api_client(endpoint: str, token: str, cafile: str) -> client.ApiClient:
    kconfig = config.kube_config.Configuration(
        host=endpoint, api_key={"authorization": "Bearer " + token}
    )
    kconfig.ssl_ca_cert = cafile
    kclient = client.ApiClient(configuration=kconfig)
    return kclient
