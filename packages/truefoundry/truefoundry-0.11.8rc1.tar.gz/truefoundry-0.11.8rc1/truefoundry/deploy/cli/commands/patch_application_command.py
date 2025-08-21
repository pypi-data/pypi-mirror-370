import json

import rich_click as click
import yaml

from truefoundry.cli.const import GROUP_CLS
from truefoundry.cli.util import handle_exception_wrapper
from truefoundry.deploy.lib.dao import application as application_lib


@click.group(
    name="patch-application",
    cls=GROUP_CLS,
    invoke_without_command=True,
    help="Deploy application with patches to TrueFoundry",
)
@click.option(
    "-f",
    "--patch-file",
    "--patch_file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="Path to yaml patch file",
    show_default=True,
)
@click.option(
    "-p",
    "--patch",
    type=click.STRING,
    help="Patch in JSON format provided as a string.",
    show_default=True,
)
@click.option(
    "-a",
    "--application_fqn",
    "--application-fqn",
    type=click.STRING,
    required=True,
    help="FQN of the Application to patch and deploy",
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
@handle_exception_wrapper
def patch_application_command(
    patch_file: str, application_fqn: str, patch: str, wait: bool
):
    from truefoundry.deploy.v2.lib.deployable_patched_models import Application

    manifest_patch_obj = None
    if not patch_file and not patch:
        raise Exception("You need to either provide --file or --patch.")
    elif patch and patch_file:
        raise Exception("You can only provide one of --file and --patch")
    elif patch:
        try:
            manifest_patch_obj = json.loads(patch)
        except json.decoder.JSONDecodeError as e:
            raise Exception("Invalid JSON provided as --patch") from e
    elif patch_file:
        with open(patch_file, "r") as f:
            manifest_patch_obj = yaml.safe_load(f)

    if not manifest_patch_obj or not isinstance(manifest_patch_obj, dict):
        raise Exception("Invalid patch, aborting deployment.")

    tfy_application = application_lib.get_application(application_fqn=application_fqn)
    patched_application_obj = application_lib.get_patched_application_definition(
        application=tfy_application, manifest_patch=manifest_patch_obj
    )

    application = Application.parse_obj(patched_application_obj)
    application.deploy(workspace_fqn=tfy_application.workspace.fqn, wait=wait)


def get_patch_application_command():
    return patch_application_command
