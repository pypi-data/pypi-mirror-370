import rich_click as click

from truefoundry.cli.const import GROUP_CLS
from truefoundry.ml.cli.commands.model_init import get_model_init_command


@click.group(
    name="deploy-init",
    cls=GROUP_CLS,
    help="Initialize the TrueFoundry deployment configuration.",
)
def deploy_init_command(): ...


def get_deploy_init_command():
    """
    Generates the deploy-init command.
        model: Initialize the TrueFoundry deployment configuration for a model. eg: tfy deploy-init model [--args]
    """

    deploy_init_command.add_command(get_model_init_command())
    return deploy_init_command
