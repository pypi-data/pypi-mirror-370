from pathlib import Path
from typing import Any, Dict, Iterator, Optional

import yaml

from truefoundry.deploy.lib.clients.servicefoundry_client import (
    ServiceFoundryServiceClient,
)
from truefoundry.deploy.lib.model.entity import DeleteResult, ManifestLike
from truefoundry.pydantic_v1 import ValidationError


def _delete_manifest(
    manifest: Dict[str, Any],
    client: Optional[ServiceFoundryServiceClient] = None,
    filename: Optional[str] = None,
    index: Optional[int] = None,
) -> DeleteResult:
    client = client or ServiceFoundryServiceClient()

    file_metadata = ""
    if index is not None:
        file_metadata += f" at index {index}"
    if filename:
        file_metadata += f" from file {filename}"

    try:
        manifest = ManifestLike.parse_obj(manifest)
    except ValidationError as ex:
        return DeleteResult(
            success=False,
            message=f"Failed to parse manifest{file_metadata}. Error: {ex}",
        )

    try:
        client.delete(manifest.dict())

        return DeleteResult(
            success=True,
            message=(
                f"Successfully deleted resource manifest {manifest.name} of type {manifest.type}."
            ),
        )
    except Exception as ex:
        return DeleteResult(
            success=False,
            message=(
                f"Failed to delete resource manifest {manifest.name} of type {manifest.type}. Error: {ex}."
            ),
        )


def delete_manifest(
    manifest: Dict[str, Any],
    client: Optional[ServiceFoundryServiceClient] = None,
) -> DeleteResult:
    return _delete_manifest(manifest=manifest, client=client)


def delete_manifest_file(
    filepath: str,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Iterator[DeleteResult]:
    client = client or ServiceFoundryServiceClient()
    filename = Path(filepath).name
    try:
        with open(filepath, "r") as f:
            manifests_it = list(yaml.safe_load_all(f))
    except Exception as ex:
        yield DeleteResult(
            success=False,
            message=f"Failed to read file {filepath} as a valid YAML file. Error: {ex}",
        )
    else:
        for index, manifest in enumerate(manifests_it):
            if not isinstance(manifest, dict):
                yield DeleteResult(
                    success=False,
                    message=f"Failed to delete resource manifest at index {index} from file {filename}. Error: A manifest must be a dict, got type {type(manifest)}",
                )
                continue

            yield _delete_manifest(
                manifest=manifest,
                client=client,
                filename=filename,
                index=index,
            )
