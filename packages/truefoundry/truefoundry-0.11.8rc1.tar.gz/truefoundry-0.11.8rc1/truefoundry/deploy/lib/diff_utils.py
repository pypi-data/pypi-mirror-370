import copy
import difflib
from typing import Any, Dict, Optional

import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel


def _normalize_manifest_for_diff(obj: Any) -> Any:
    """
    Normalize a manifest object for consistent diffing.
    Only sorts the 'integrations' field by name
    """
    if isinstance(obj, dict):
        _type = obj.get("type") or ""
        integrations = obj.get("integrations")
        if (
            _type.startswith("provider-account/")
            and isinstance(integrations, list)
            and all(isinstance(item, dict) and "name" in item for item in integrations)
        ):
            result = copy.deepcopy(obj)
            result["integrations"] = sorted(integrations, key=lambda x: x["name"])
            return result
    return obj


def format_manifest_for_diff(manifest: Dict[str, Any]) -> str:
    """
    Format a manifest for diffing with consistent formatting.

    Args:
        manifest: The manifest dictionary to format

    Returns:
        A consistently formatted YAML string suitable for diffing
    """
    # Normalize the manifest for diffing
    normalized_manifest = _normalize_manifest_for_diff(manifest)
    return yaml.dump(normalized_manifest, sort_keys=True, indent=2)


def generate_manifest_diff(
    existing_manifest: Dict[str, Any],
    new_manifest: Dict[str, Any],
    manifest_name: str = "manifest",
) -> Optional[str]:
    """
    Generate a unified diff between existing and new manifests.

    Args:
        existing_manifest: The existing manifest of the resource
        new_manifest: The new manifest being applied
        manifest_name: Name of the manifest for diff headers

    Returns:
        Unified diff string if there are differences, None if no differences
    """
    # Format both manifests consistently
    existing_formatted = format_manifest_for_diff(existing_manifest)
    new_formatted = format_manifest_for_diff(new_manifest)

    # Generate diff
    existing_lines = existing_formatted.splitlines(keepends=True)
    new_lines = new_formatted.splitlines(keepends=True)
    diff_lines = list(
        difflib.unified_diff(
            existing_lines,
            new_lines,
            fromfile=f"existing/{manifest_name}",
            tofile=f"new/{manifest_name}",
        )
    )

    if not diff_lines:
        return None

    return "".join(diff_lines)


def print_manifest_diff(
    existing_manifest: Dict[str, Any],
    new_manifest: Dict[str, Any],
    manifest_name: str = "manifest",
    console: Optional[Console] = None,
) -> bool:
    """
    Generate and print a colored diff between manifests.

    Args:
        existing_manifest: The existing manifest of the resource
        new_manifest: The new manifest being applied
        manifest_name: Name of the manifest for diff headers
        console: Optional Rich console instance to use for printing

    Returns:
        True if diff was printed, False if no diff
    """
    if console is None:
        console = Console()

    diff_text = generate_manifest_diff(existing_manifest, new_manifest, manifest_name)

    if diff_text is None:
        console.print(f"[green]No changes detected for {manifest_name}[/]")
        return False

    console.print(
        Panel(Markdown(f"```diff\n{diff_text}\n```"), title=f"Diff for {manifest_name}")
    )
    console.print()
    return True
