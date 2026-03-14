"""Extract cluster API URL and bearer token from kubeconfig.

Falls back to ``kubectl create token`` when the kubeconfig uses
certificate auth and no bearer token is available.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)

_SA_TOKEN_NAMESPACE = "openshift-cluster-version"
_SA_TOKEN_NAME = "default"
_SA_TOKEN_DURATION = "168h"


@dataclass
class KubeCredentials:
    """Kubernetes API server URL and bearer token."""

    api_url: str
    token: str


def _create_sa_token(kubeconfig: str | None = None) -> str | None:
    """Create a ServiceAccount token via ``kubectl create token``.

    Targets the *default* SA in *openshift-cluster-version* which has
    cluster-admin privileges on OpenShift clusters.  Returns the raw
    token string, or ``None`` if kubectl is unavailable or the command
    fails (e.g. non-OpenShift cluster, missing SA, RBAC denial).
    """
    kubectl = shutil.which("kubectl")
    if not kubectl:
        logger.debug("kubectl not found in PATH -- cannot create SA token")
        return None

    env = dict(os.environ)
    if kubeconfig:
        env["KUBECONFIG"] = kubeconfig

    cmd = [
        kubectl,
        "create",
        "token",
        _SA_TOKEN_NAME,
        "-n",
        _SA_TOKEN_NAMESPACE,
        f"--duration={_SA_TOKEN_DURATION}",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        logger.warning("kubectl create token failed: %s", exc)
        return None

    if result.returncode != 0:
        stderr = result.stderr.strip()
        logger.warning("kubectl create token exited %d: %s", result.returncode, stderr)
        return None

    token = result.stdout.strip()
    if not token:
        logger.warning("kubectl create token returned empty output")
        return None

    logger.info(
        "Obtained SA token for %s/%s (duration %s)",
        _SA_TOKEN_NAMESPACE,
        _SA_TOKEN_NAME,
        _SA_TOKEN_DURATION,
    )
    return token


def load_kubeconfig(
    kubeconfig: str | None = None,
    context: str | None = None,
) -> KubeCredentials | None:
    """Load credentials from a kubeconfig file using the official k8s client.

    Token resolution (in order):

    1. Bearer token from the loaded ``Configuration`` (covers inline tokens,
       exec credential plugins, auth-provider/OIDC, token files, etc.).
    2. Fallback: ``kubectl create token`` to mint a ServiceAccount token
       using the certificate auth already present in the kubeconfig.  This
       handles OpenShift ``kubeadmin`` configs that rely on client certs.

    Returns ``None`` when the file is missing, no token can be obtained,
    or the ``kubernetes`` package is not installed.
    """
    try:
        from kubernetes import config as k8s_config
        from kubernetes.client import Configuration
    except ImportError:
        logger.warning(
            "kubernetes package not installed — cannot read kubeconfig. "
            "Install it with:  pip install kubernetes"
        )
        return None

    try:
        k8s_config.load_kube_config(
            config_file=kubeconfig,
            context=context,
        )
    except Exception as exc:
        logger.warning("Failed to load kubeconfig: %s", exc)
        return None

    cfg = Configuration.get_default_copy()

    api_url = (cfg.host or "").rstrip("/")
    if not api_url:
        logger.debug("Kubeconfig loaded but no API server URL found")
        return None

    token = (cfg.api_key.get("authorization") or "").removeprefix("Bearer ")

    if not token:
        logger.info("No token in kubeconfig, trying kubectl create token...")
        token = _create_sa_token(kubeconfig) or ""

    if not token:
        logger.warning(
            "Kubeconfig loaded (server: %s) but no token could be obtained. "
            "Cluster may use certificate auth -- pass --kube-token or set KUBE_TOKEN.",
            api_url,
        )
        return None

    logger.info("Using kubeconfig (server: %s)", api_url)
    return KubeCredentials(api_url=api_url, token=token)
