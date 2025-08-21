import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import rich_click as click

from truefoundry.cli.const import COMMAND_CLS
from truefoundry.cli.util import handle_exception_wrapper
from truefoundry.common.session import Session
from truefoundry.deploy.cli.commands.utils import (
    CONTEXT_NAME_FORMAT,
    get_cluster_server_url,
    get_kubeconfig_content,
    get_kubeconfig_path,
)
from truefoundry.deploy.io.no_output_callback import NoOutputCallBack
from truefoundry.deploy.lib.session import login


@click.command(
    name="k8s-exec-credential",
    cls=COMMAND_CLS,
    help="Generate a Kubernetes exec credential for the specified cluster user",
)
@click.option(
    "-c",
    "--cluster",
    type=str,
    required=True,
    help="The cluster id from TrueFoundry",
)
@handle_exception_wrapper
def k8s_exec_credential_command(cluster: str) -> None:
    """
    Generate a Kubernetes exec credential for the specified cluster.
    This command retrieves the cluster server URL from the kubeconfig file,
    """
    path = get_kubeconfig_path()
    kubeconfig: Dict[str, Any] = get_kubeconfig_content(path=path)
    server_url: Optional[str] = get_cluster_server_url(kubeconfig, cluster)
    if not server_url:
        raise click.ClickException(
            f"\nContext {CONTEXT_NAME_FORMAT.format(cluster=cluster)!r} for cluster {cluster!r} not found in kubeconfig. \n\nPlease run 'tfy get kubeconfig --cluster {cluster}' first."
        )
    host: str = f"{urlparse(server_url).scheme}://{urlparse(server_url).netloc}"
    login(host=host, output_hook=NoOutputCallBack())

    session = Session.new()
    token: str = session.access_token

    exec_credential: Dict[str, Any] = {
        "kind": "ExecCredential",
        "apiVersion": "client.authentication.k8s.io/v1beta1",
        "spec": {},
        "status": {
            "expirationTimestamp": datetime.fromtimestamp(
                session.token.exp, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "token": token,
        },
    }

    print(json.dumps(exec_credential, indent=4))
