import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

DEFAULT_KUBECONFIG_PATH: Path = Path.home() / ".kube" / "config"
CLUSTER_NAME_FORMAT: str = "tfy-{cluster}-cluster"
USER_NAME_FORMAT: str = "tfy-{cluster}-user"
CONTEXT_NAME_FORMAT: str = "tfy-{cluster}-context"
KUBE_CONFIG_CONTENT = {
    "apiVersion": "v1",
    "kind": "Config",
    "clusters": [],
    "users": [],
    "contexts": [],
}


def get_kubeconfig_path() -> Path:
    """
    Returns the kubeconfig path to use.
    If KUBECONFIG is set, returns the first path from the environment variable.
    Otherwise, returns the default kubeconfig path.
    """
    kubeconfig_env = os.environ.get("KUBECONFIG")
    if kubeconfig_env:
        # Use the first path in KUBECONFIG if multiple are provided
        first_path = kubeconfig_env.split(os.pathsep)[0]
        return Path(first_path)
    return DEFAULT_KUBECONFIG_PATH


def get_kubeconfig_content(path: Path = DEFAULT_KUBECONFIG_PATH) -> Dict[str, Any]:
    if path.exists():
        with open(path, "r") as f:
            return yaml.safe_load(f) or KUBE_CONFIG_CONTENT
    else:
        return KUBE_CONFIG_CONTENT


def save_kubeconfig(config: Dict[str, Any], path: Path) -> None:
    config["apiVersion"] = "v1"
    config["kind"] = "Config"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False)


def add_update_cluster_context(
    config: Dict[str, Any],
    cluster: str,
    server_url: str,
    exec_command: List[str],
    envs: Optional[Dict[str, str]] = None,
) -> str:
    """
    Adds a new cluster context to the given kubeconfig dictionary using exec-based authentication.
    """
    cluster_name: str = CLUSTER_NAME_FORMAT.format(cluster=cluster)
    user_name: str = USER_NAME_FORMAT.format(cluster=cluster)
    context_name: str = CONTEXT_NAME_FORMAT.format(cluster=cluster)

    # Add or update cluster
    config["clusters"] = [
        c for c in config.get("clusters", []) if c["name"] != cluster_name
    ]
    config["clusters"].append(
        {
            "name": cluster_name,
            "cluster": {"server": server_url},
        }
    )

    # Add or update user with exec command
    config["users"] = [u for u in config.get("users", []) if u["name"] != user_name]
    config["users"].append(
        {
            "name": user_name,
            "user": {
                "exec": {
                    "apiVersion": "client.authentication.k8s.io/v1beta1",
                    "command": exec_command[0],
                    "args": exec_command[1:],
                    "env": (
                        [{"name": k, "value": v} for k, v in envs.items()]
                        if envs
                        else []
                    ),
                }
            },
        }
    )

    # Add or update context
    config["contexts"] = [
        c for c in config.get("contexts", []) if c["name"] != context_name
    ]
    config["contexts"].append(
        {"name": context_name, "context": {"cluster": cluster_name, "user": user_name}}
    )
    return context_name


def get_cluster_context(
    config: Dict[str, Any], cluster: str
) -> Optional[Dict[str, Any]]:
    cluster_name: str = CLUSTER_NAME_FORMAT.format(cluster=cluster)
    return next(
        (c for c in config.get("clusters", []) if c["name"] == cluster_name), None
    )


def get_cluster_server_url(config: Dict[str, Any], cluster: str) -> Optional[str]:
    cluster_context: Optional[Dict[str, Any]] = get_cluster_context(config, cluster)
    if cluster_context:
        return cluster_context["cluster"].get("server")
    return None
