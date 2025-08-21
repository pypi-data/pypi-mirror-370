from pathlib import Path
from typing import Any, Dict, Iterator, Optional

import yaml

from truefoundry.cli.console import console
from truefoundry.deploy.lib.clients.servicefoundry_client import (
    ServiceFoundryServiceClient,
)
from truefoundry.deploy.lib.diff_utils import print_manifest_diff
from truefoundry.deploy.lib.model.entity import ApplyResult, ManifestLike
from truefoundry.pydantic_v1 import ValidationError


def _apply_manifest(
    manifest: Dict[str, Any],
    client: Optional[ServiceFoundryServiceClient] = None,
    filename: Optional[str] = None,
    index: Optional[int] = None,
    dry_run: bool = False,
    show_diff: bool = False,
) -> ApplyResult:
    client = client or ServiceFoundryServiceClient()

    file_metadata = ""
    if index is not None:
        file_metadata += f" at index {index}"
    if filename:
        file_metadata += f" from file {filename}"

    try:
        parsed_manifest = ManifestLike.parse_obj(manifest)
    except ValidationError as ex:
        return ApplyResult(
            success=False,
            message=f"Failed to apply manifest{file_metadata}. Error: {ex}",
        )

    prefix = "[Dry Run] " if dry_run else ""
    suffix = " (No changes were applied)" if dry_run else ""

    try:
        api_response = client.apply(parsed_manifest.dict(), dry_run)

        # Show diff for dry runs only when show_diff is enabled
        if dry_run and show_diff and api_response.existing_manifest:
            print_manifest_diff(
                existing_manifest=api_response.existing_manifest,
                new_manifest=parsed_manifest.dict(),
                manifest_name=f"{parsed_manifest.name} ({parsed_manifest.type})",
                console=console,
            )

        return ApplyResult(
            success=True,
            message=(
                f"{prefix}Successfully configured manifest {parsed_manifest.name} of type {parsed_manifest.type}.{suffix}"
            ),
        )
    except Exception as ex:
        return ApplyResult(
            success=False,
            message=(
                f"{prefix}Failed to apply manifest {parsed_manifest.name} of type {parsed_manifest.type}. Error: {ex}.{suffix}"
            ),
        )


def apply_manifest(
    manifest: Dict[str, Any],
    client: Optional[ServiceFoundryServiceClient] = None,
    dry_run: bool = False,
    show_diff: bool = False,
) -> ApplyResult:
    return _apply_manifest(
        manifest=manifest, client=client, dry_run=dry_run, show_diff=show_diff
    )


def apply_manifest_file(
    filepath: str,
    client: Optional[ServiceFoundryServiceClient] = None,
    dry_run: bool = False,
    show_diff: bool = False,
) -> Iterator[ApplyResult]:
    client = client or ServiceFoundryServiceClient()
    filename = Path(filepath).name
    try:
        with open(filepath, "r") as f:
            manifests_it = list(yaml.safe_load_all(f))
    except Exception as ex:
        yield ApplyResult(
            success=False,
            message=f"Failed to read file {filepath} as a valid YAML file. Error: {ex}",
        )
    else:
        prefix = "[Dry Run] " if dry_run else ""
        for index, manifest in enumerate(manifests_it):
            if not isinstance(manifest, dict):
                yield ApplyResult(
                    success=False,
                    message=f"{prefix}Failed to apply manifest at index {index} from file {filename}. Error: A manifest must be a dict, got type {type(manifest)}",
                )
                continue

            yield _apply_manifest(
                manifest=manifest,
                client=client,
                filename=filename,
                index=index,
                dry_run=dry_run,
                show_diff=show_diff,
            )
