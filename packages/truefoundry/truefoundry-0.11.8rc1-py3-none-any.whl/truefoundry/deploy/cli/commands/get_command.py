import rich_click as click

from truefoundry.cli.const import GROUP_CLS
from truefoundry.common.utils import is_internal_env_set
from truefoundry.deploy.cli.commands.k8s_exec_credential_command import (
    k8s_exec_credential_command,
)
from truefoundry.deploy.cli.commands.kubeconfig_command import kubeconfig_command

# TODO (chiragjn): --json should disable all non json console prints


@click.group(name="get", cls=GROUP_CLS)
def get_command():
    # TODO (chiragjn): Figure out a way to update supported resources based on ENABLE_* flags
    """
    Get TrueFoundry resources

    \b
    Supported resources:
    - Kubeconfig
    """
    pass


def get_get_command():
    get_command.add_command(kubeconfig_command)
    if is_internal_env_set():
        get_command.add_command(k8s_exec_credential_command)
    return get_command
