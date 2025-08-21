from typing import List, Tuple

import rich_click as click

from truefoundry.cli.config import CliConfig
from truefoundry.cli.console import console
from truefoundry.cli.const import COMMAND_CLS, GROUP_CLS
from truefoundry.cli.display_util import print_json
from truefoundry.cli.util import handle_exception_wrapper
from truefoundry.deploy.io.rich_output_callback import RichOutputCallBack
from truefoundry.deploy.lib.clients.servicefoundry_client import (
    ServiceFoundryServiceClient,
)
from truefoundry.deploy.lib.dao import application as application_lib
from truefoundry.deploy.lib.dao import delete as delete_lib
from truefoundry.deploy.lib.dao import workspace as workspace_lib
from truefoundry.deploy.lib.messages import (
    PROMPT_DELETED_APPLICATION,
    PROMPT_DELETED_WORKSPACE,
    PROMPT_DELETING_MANIFEST,
)
from truefoundry.deploy.lib.model.entity import DeleteResult

# TODO (chiragjn): --json should disable all non json console prints


@click.group(name="delete", cls=GROUP_CLS, invoke_without_command=True)
@click.pass_context
@click.option(
    "-f",
    "--file",
    "files",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="Path to yaml manifest file (You can pass multiple files at once by providing multiple -f options)",
    show_default=True,
    required=False,
    multiple=True,
)
@handle_exception_wrapper
def delete_command(ctx, files: Tuple[str, ...]):
    """
    Delete TrueFoundry resources
    """
    if ctx.invoked_subcommand is None:
        if not files:
            raise click.UsageError("Missing option '-f' / '--file'")
        delete_results: List[DeleteResult] = []
        client = ServiceFoundryServiceClient()
        for file in files:
            with console.status(PROMPT_DELETING_MANIFEST.format(file), spinner="dots"):
                for delete_result in delete_lib.delete_manifest_file(file, client):
                    if delete_result.success:
                        console.print(f"[green]\u2714 {delete_result.message}[/]")
                    else:
                        console.print(f"[red]\u2718 {delete_result.message}[/]")

                    delete_results.append(delete_result)

        if not all(delete_result.success for delete_result in delete_results):
            raise Exception("Failed to delete one or more resource manifests")


@click.command(name="workspace", cls=COMMAND_CLS, help="Delete a Workspace")
@click.option(
    "-w",
    "--workspace-fqn",
    "--workspace_fqn",
    type=click.STRING,
    default=None,
    help="FQN of the Workspace to delete",
    required=True,
)
@click.confirmation_option(prompt="Are you sure you want to delete this workspace?")
@handle_exception_wrapper
def delete_workspace(workspace_fqn):
    deleted_workspace = workspace_lib.delete_workspace(
        workspace_fqn=workspace_fqn,
    )
    output_hook = RichOutputCallBack()
    output_hook.print_line(PROMPT_DELETED_WORKSPACE.format(workspace_fqn))
    if CliConfig.json:
        print_json(data=deleted_workspace.dict())


@click.command(name="application", cls=COMMAND_CLS, help="Delete an Application")
@click.option(
    "--application-fqn",
    "--application_fqn",
    type=click.STRING,
    default=None,
    help="FQN of the Application to delete",
    required=True,
)
@click.confirmation_option(prompt="Are you sure you want to delete this application?")
@handle_exception_wrapper
def delete_application(application_fqn):
    response = application_lib.delete_application(
        application_fqn=application_fqn,
    )
    output_hook = RichOutputCallBack()
    output_hook.print_line(PROMPT_DELETED_APPLICATION.format(application_fqn))
    if CliConfig.json:
        print_json(data=response)


def get_delete_command():
    delete_command.add_command(delete_workspace)
    delete_command.add_command(delete_application)
    return delete_command
