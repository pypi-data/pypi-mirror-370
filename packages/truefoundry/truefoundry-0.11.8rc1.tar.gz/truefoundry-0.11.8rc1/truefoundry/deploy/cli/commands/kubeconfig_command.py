from typing import Any, Dict, Optional
from urllib.parse import urljoin

import rich_click as click
from rich.console import Console

from truefoundry.cli.const import COMMAND_CLS
from truefoundry.cli.util import handle_exception_wrapper, select_cluster
from truefoundry.common.session import Session
from truefoundry.deploy.cli.commands.utils import (
    CONTEXT_NAME_FORMAT,
    add_update_cluster_context,
    get_cluster_server_url,
    get_kubeconfig_content,
    get_kubeconfig_path,
    save_kubeconfig,
)

console = Console()


def _construct_k8s_proxy_server(host: str, cluster: str) -> str:
    """
    Construct the Kubernetes proxy server URL.
    """
    return urljoin(host, f"api/svc/v1/k8s/proxy/{cluster}")


def _should_update_existing_context(cluster: str, kubeconfig: Dict[str, Any]) -> bool:
    """
    Prompt the user whether to overwrite an existing kubeconfig context.
    """
    server_url = get_cluster_server_url(kubeconfig, cluster)
    if server_url is not None:
        console.print(
            f"\nContext {CONTEXT_NAME_FORMAT.format(cluster=cluster)!r} for cluster {cluster!r} already exists in kubeconfig.\n"
        )
        return click.confirm(
            text="Do you want to update the context?", default=False, err=True
        )
    return True


@click.command(name="kubeconfig", cls=COMMAND_CLS)
@click.option(
    "-c",
    "--cluster",
    type=str,
    required=False,
    help="The cluster id from TrueFoundry. If not provided, an interactive prompt will list available clusters",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    show_default=True,
    help="Overwrites existing cluster entry without prompting",
)
@handle_exception_wrapper
def kubeconfig_command(cluster: Optional[str] = None, overwrite: bool = False) -> None:
    """
    Update kubeconfig file to access cluster attached to TrueFoundry Control Plane.

    By default, credentials are written to ~/.kube/config. You can provide an alternate path by setting the KUBECONFIG environment variable. If KUBECONFIG contains multiple paths, the first one is used.
    """
    session = Session.new()
    cluster = select_cluster(cluster)

    path = get_kubeconfig_path()
    kubeconfig = get_kubeconfig_content(path=path)

    if not overwrite and not _should_update_existing_context(cluster, kubeconfig):
        console.print(
            "Existing context found. Use '--overwrite' to force update the context."
        )
        return

    k8s_proxy_server = _construct_k8s_proxy_server(session.tfy_host, cluster)
    context_name = add_update_cluster_context(
        kubeconfig,
        cluster,
        k8s_proxy_server,
        exec_command=[
            "tfy",
            "--json",
            "get",
            "k8s-exec-credential",
            "--cluster",
            cluster,
        ],
        envs={"TFY_INTERNAL": "1"},
    )

    save_kubeconfig(kubeconfig, path=path)
    console.print(
        f"\nUpdated kubeconfig at {str(path)!r} with context {context_name!r} for cluster {cluster!r}\n\n"
        f"Run 'kubectl config use-context {context_name}' to use this context.\n"
    )
