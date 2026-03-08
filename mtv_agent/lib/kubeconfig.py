"""Extract cluster API URL and bearer token via the official k8s client."""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class KubeCredentials:
    """Kubernetes API server URL and bearer token."""

    api_url: str
    token: str


def load_kubeconfig(
    kubeconfig: str | None = None,
    context: str | None = None,
) -> KubeCredentials | None:
    """Load credentials from a kubeconfig file using the official k8s client.

    Handles all auth methods the upstream client supports: bearer tokens,
    exec credential plugins, auth-provider (OIDC/GCP), token files, etc.

    Returns ``None`` when the file is missing, the context has no
    extractable bearer token, or the ``kubernetes`` package is not installed.
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
    token = (cfg.api_key.get("authorization") or "").removeprefix("Bearer ")

    if not api_url or not token:
        logger.debug(
            "Kubeconfig loaded but missing data: api_url=%s, token=%s",
            bool(api_url),
            bool(token),
        )
        return None

    logger.info("Using kubeconfig (server: %s)", api_url)
    return KubeCredentials(api_url=api_url, token=token)
