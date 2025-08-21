import os
import sys
from typing import Optional

import rich_click as click
import yaml
from click import UsageError
from click.exceptions import ClickException

from truefoundry.autodeploy.cli import cli as autodeploy_cli
from truefoundry.autodeploy.exception import InvalidRequirementsException
from truefoundry.cli.const import COMMAND_CLS, GROUP_CLS
from truefoundry.cli.util import handle_exception_wrapper


def _get_default_spec_file():
    paths = [
        "./truefoundry.yaml",
        "./truefoundry.yml",
        "./servicefoundry.yaml",
        "./servicefoundry.yml",
    ]
    for path in paths:
        if os.path.exists(path):
            return path


@click.group(
    name="deploy",
    cls=GROUP_CLS,
    invoke_without_command=True,
    help="Deploy application to TrueFoundry",
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    default=_get_default_spec_file(),
    help="Path to truefoundry.yaml file",
    show_default=True,
)
@click.option(
    "-w",
    "--workspace-fqn",
    "--workspace_fqn",
    default=None,
    help="FQN of the Workspace to deploy to. If not provided, the Workspace FQN will be read from the deployment spec if available.",
)
@click.option(
    "--wait/--no-wait",
    # The leading space is intentional. See: https://github.com/pallets/click/blob/2d610e36a429bfebf0adb0ca90cdc0585f296369/docs/options.md?plain=1#L295
    " /--no_wait",
    is_flag=True,
    show_default=True,
    default=True,
    help="Wait and tail the deployment progress",
)
@click.option(
    "--force/--no-force",
    is_flag=True,
    show_default=True,
    default=False,
    help="Force create a new deployment by canceling any ongoing deployments",
)
@click.option(
    "--trigger-on-deploy/--no-trigger-on-deploy",
    "--trigger_on_deploy/--no_trigger_on_deploy",
    is_flag=True,
    show_default=True,
    default=False,
    help="Trigger a Job run after deployment succeeds. Has no effect for non Job type deployments",
)
@click.pass_context
@handle_exception_wrapper
def deploy_command(
    ctx: click.Context,
    file: str,
    workspace_fqn: Optional[str],
    wait: bool,
    force: bool = False,
    trigger_on_deploy: bool = False,
):
    if ctx.invoked_subcommand is not None:
        return
    from truefoundry.common.session import Session
    from truefoundry.deploy.v2.lib.deployable_patched_models import Application

    try:
        _ = Session.new()
    except Exception as e:
        raise ClickException(message=str(e)) from e

    if file:
        with open(file, "r") as f:
            application_definition = yaml.safe_load(f)

        application = Application.parse_obj(application_definition)
        application.deploy(
            workspace_fqn=workspace_fqn,
            wait=wait,
            force=force,
            trigger_on_deploy=trigger_on_deploy,
        )
        sys.exit(0)

    click.echo(
        click.style(
            "We did not find any truefoundry.yaml or servicefoundry.yaml at the root path.",
            fg="red",
        ),
        color=True,
    )

    if not sys.stdout.isatty():
        click.echo(
            click.style(
                'Please create a truefoundry.yaml or pass the file name with "--file file_name"',
                fg="yellow",
            ),
            color=True,
        )
        sys.exit(1)

    try:
        autodeploy_cli(project_root_path=".", deploy=True, workspace_fqn=workspace_fqn)
    except InvalidRequirementsException as e:
        raise UsageError(message=e.message) from e
    except Exception as e:
        raise UsageError(message=str(e)) from e


@deploy_command.command(name="workflow", cls=COMMAND_CLS, help="Deploy a Workflow")
@click.option(
    "-n",
    "--name",
    required=True,
    help="Name of the Workflow",
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    required=True,
    help="Path to the Workflow file. e.g. workflow.py",
)
@click.option(
    "-w",
    "--workspace-fqn",
    "--workspace_fqn",
    required=True,
    help="FQN of the Workspace to deploy to.",
)
@handle_exception_wrapper
def deploy_workflow_command(name: str, file: str, workspace_fqn: str):
    from truefoundry.common.session import Session

    try:
        _ = Session.new()
    except Exception as e:
        raise ClickException(message=str(e)) from e

    from truefoundry.deploy.v2.lib.deployable_patched_models import Workflow

    workflow = Workflow(
        name=name,
        workflow_file_path=file,
    )
    workflow.deploy(workspace_fqn=workspace_fqn)


def get_deploy_command():
    return deploy_command
