from typing import List, Tuple

import rich_click as click

from truefoundry.cli.console import console
from truefoundry.cli.const import GROUP_CLS
from truefoundry.cli.util import handle_exception_wrapper
from truefoundry.deploy.lib.clients.servicefoundry_client import (
    ServiceFoundryServiceClient,
)
from truefoundry.deploy.lib.dao import apply as apply_lib
from truefoundry.deploy.lib.messages import PROMPT_APPLYING_MANIFEST
from truefoundry.deploy.lib.model.entity import ApplyResult


@click.group(
    name="apply",
    cls=GROUP_CLS,
    invoke_without_command=True,
    help="Create resources by applying manifest locally from TrueFoundry spec",
    context_settings={"ignore_unknown_options": True, "allow_interspersed_args": True},
)
@click.option(
    "-f",
    "--file",
    "files",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="Path to yaml manifest file (You can apply multiple files at once by providing multiple -f options)",
    show_default=True,
    required=True,
    multiple=True,
)
@click.option(
    "--dry-run",
    "--dry_run",
    is_flag=True,
    show_default=True,
    help="Simulate the process without actually applying the manifest",
)
@click.option(
    "--show-diff",
    "--show_diff",
    is_flag=True,
    show_default=True,
    help="Print manifest differences when using --dry-run",
)
@handle_exception_wrapper
def apply_command(
    files: Tuple[str, ...], dry_run: bool = False, show_diff: bool = False
):
    # Validate that show_diff is only used with dry_run
    if show_diff and not dry_run:
        raise click.ClickException("--show-diff requires --dry-run")

    apply_results: List[ApplyResult] = []
    client = ServiceFoundryServiceClient()
    for file in files:
        with console.status(PROMPT_APPLYING_MANIFEST.format(file), spinner="dots"):
            for apply_result in apply_lib.apply_manifest_file(
                file, client, dry_run, show_diff
            ):
                if apply_result.success:
                    console.print(f"[green]\u2714 {apply_result.message}[/]")
                else:
                    console.print(f"[red]\u2718 {apply_result.message}[/]")

                apply_results.append(apply_result)

    if not all(apply_result.success for apply_result in apply_results):
        raise Exception("Failed to apply one or more manifests")


def get_apply_command():
    return apply_command
