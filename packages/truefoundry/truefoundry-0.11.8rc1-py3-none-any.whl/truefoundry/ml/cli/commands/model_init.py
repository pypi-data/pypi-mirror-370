import os
from typing import Optional

import rich_click as click

from truefoundry.cli.console import console
from truefoundry.cli.const import COMMAND_CLS
from truefoundry.cli.util import handle_exception_wrapper
from truefoundry.ml._autogen.client import ModelServer  # type: ignore[attr-defined]
from truefoundry.ml.cli.utils import (
    AppName,
    NonEmptyString,
)
from truefoundry.ml.mlfoundry_api import get_client


@click.command(
    name="model",
    cls=COMMAND_CLS,
    help="Generating application code for the specified model version.",
)
@click.option(
    "--name",
    required=True,
    type=AppName(),
    help="Name for the model server deployment",
    show_default=True,
)
@click.option(
    "--model-version-fqn",
    "--model_version_fqn",
    type=NonEmptyString(),
    required=True,
    show_default=True,
    help="Fully Qualified Name (FQN) of the model version to deploy, e.g., 'model:tenant_name/my-model/linear-regression:2'",
)
@click.option(
    "-w",
    "--workspace-fqn",
    "--workspace_fqn",
    type=NonEmptyString(),
    required=True,
    show_default=True,
    help="Fully Qualified Name (FQN) of the workspace to deploy",
)
@click.option(
    "--model-server",
    "--model_server",
    type=click.Choice(ModelServer, case_sensitive=False),
    default=ModelServer.FASTAPI.value,
    show_default=True,
    help="Specify the model server (Case Insensitive).",
)
@click.option(
    "--output-dir",
    "--output_dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    help="Output directory for the model server code",
    required=False,
    show_default=True,
    default=os.getcwd(),
)
@handle_exception_wrapper
def model_init_command(
    name: str,
    model_version_fqn: str,
    workspace_fqn: str,
    model_server: ModelServer,
    output_dir: Optional[str],
):
    """
    Generates application code for the specified model version.
    """
    ml_client = get_client()
    console.print(f"Generating application code for {model_version_fqn!r}")
    output_dir = ml_client._initialize_model_server(
        name=name,
        model_version_fqn=model_version_fqn,
        workspace_fqn=workspace_fqn,
        model_server=ModelServer[model_server.upper()],
        output_dir=output_dir,
    )
    message = f"""
[bold green]Model Server code initialized successfully![/bold green]

[bold]Code Location:[/bold] {output_dir}

[bold]Next Steps:[/bold]
- Navigate to the model server directory:
[green]cd {output_dir}[/green]
- Refer to the README file in the directory for further instructions.
"""
    console.print(message)


def get_model_init_command():
    return model_init_command
