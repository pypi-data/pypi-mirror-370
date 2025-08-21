from typing import Optional

import click

from truefoundry.cli.const import COMMAND_CLS, GROUP_CLS
from truefoundry.ml import get_client


@click.group(
    name="download",
    cls=GROUP_CLS,
    help="Download artifact/model versions logged with TrueFoundry",
)
def download(): ...


@download.command(
    name="model",
    cls=COMMAND_CLS,
    help="Download a model version logged with TrueFoundry",
)
@click.option(
    "--fqn",
    required=True,
    type=str,
    help="fqn of the model version",
)
@click.option(
    "--path",
    type=click.Path(file_okay=False, dir_okay=True, exists=True),
    default="./",
    show_default=True,
    help="path where the model files will be downloaded",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="flag to overwrite any existing files in the `path` directory",
)
@click.option(
    "--progress/--no-progress",
    is_flag=True,
    show_default=True,
    default=None,
    help="If to show progress bar when downloading contents",
)
def model(fqn: str, path: str, overwrite: bool, progress: Optional[bool] = None):
    """
    Download the files of logged model.\n
    """
    client = get_client()
    model_version = client.get_model_version_by_fqn(fqn=fqn)
    download_path = model_version.download(
        path=path, overwrite=overwrite, progress=progress
    )
    print(f"Downloaded model files to {download_path}")


@download.command(
    name="artifact",
    cls=COMMAND_CLS,
    short_help="Download a artifact version logged with TrueFoundry",
)
@click.option(
    "--fqn",
    required=True,
    type=str,
    help="fqn of the artifact version",
)
@click.option(
    "--path",
    type=click.Path(file_okay=False, dir_okay=True, exists=True),
    default="./",
    show_default=True,
    help="path where the artifact files will be downloaded",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="flag to overwrite any existing files in the `path` directory",
)
@click.option(
    "--progress/--no-progress",
    is_flag=True,
    show_default=True,
    default=None,
    help="If to show progress bar when downloading contents",
)
def artifact(fqn: str, path: str, overwrite: bool, progress: Optional[bool] = None):
    """
    Download the files of logged artifact.\n
    """
    client = get_client()
    artifact_version = client.get_artifact_version_by_fqn(fqn=fqn)
    download_path = artifact_version.download(
        path=path, overwrite=overwrite, progress=progress
    )
    print(f"Downloaded artifact files to {download_path}")
