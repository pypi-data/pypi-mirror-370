import functools
import sys
import zipfile
from typing import Dict, Optional

import questionary
import rich_click as click
from packaging.version import parse as parse_version
from requests.exceptions import ConnectionError, Timeout
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table

from truefoundry.cli.config import CliConfig
from truefoundry.cli.console import console
from truefoundry.common.exceptions import HttpRequestException

try:
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata


_CLICK_VERSION = None


def setup_rich_click():
    click.rich_click.STYLE_ERRORS_SUGGESTION = "blue italic"
    click.rich_click.SHOW_ARGUMENTS = True
    click.rich_click.USE_RICH_MARKUP = True
    click.rich_click.STYLE_HELPTEXT = ""


def handle_exception(exception):
    if CliConfig.debug:
        console.print_exception(show_locals=True)
    if isinstance(exception, HttpRequestException):
        print_dict_as_table_panel(
            {
                "Status Code": str(exception.status_code),
                "Error": escape(exception.message),
            },
            title="Command Failed",
            border_style="red",
        )
    elif isinstance(exception, Timeout):
        loc = ""
        if exception.request:
            loc = f" at {exception.request.url}"
        print_dict_as_table_panel(
            {"Error": f"Request to TrueFoundry{loc} timed out."},
            title="Command Failed",
            border_style="red",
        )
    elif isinstance(exception, ConnectionError):
        loc = ""
        if exception.request:
            loc = f" at {exception.request.url}"
        print_dict_as_table_panel(
            {
                "Error": f"Couldn't connect to TrueFoundry{loc}. Please make sure that the provided `--host` is correct."
            },
            title="Command Failed",
            border_style="red",
        )
    elif isinstance(exception, KeyError):
        # KeyError messages in Python just suck - they tell you the key that was missing, but not the context
        console.print_exception(show_locals=False, max_frames=1)
    else:
        print_dict_as_table_panel(
            {"Error": escape(str(exception))},
            title="Command Failed",
            border_style="red",
        )


def handle_exception_wrapper(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            handle_exception(e)
            sys.exit(1)

    return inner


def print_error(message):
    text = Padding(message, (0, 1))
    console.print(
        Panel(
            text,
            border_style="red",
            title="Command failed",
            title_align="left",
            width=click.rich_click.MAX_WIDTH,
        )
    )


def print_message(message):
    text = Padding(message, (0, 1))
    console.print(
        Panel(
            text,
            border_style="cyan",
            title="Success",
            title_align="left",
            width=click.rich_click.MAX_WIDTH,
        )
    )


def print_dict_as_table_panel(
    dct: Dict[str, str],
    title: str,
    border_style: str = "cyan",
    key_color: str = "cyan",
):
    table = Table(show_header=False, box=None)
    table.add_column("Key", style=f"bold {key_color}", width=15)
    table.add_column("Value", overflow="fold")
    for key, value in dct.items():
        table.add_row(key, value)
    console.print(
        Panel(
            table,
            border_style=border_style,
            title=title,
            title_align="left",
            width=click.rich_click.MAX_WIDTH,
        )
    )


def unzip_package(path_to_package, destination):
    with zipfile.ZipFile(path_to_package, "r") as zip_ref:
        zip_ref.extractall(destination)


def prompt_if_no_value_and_supported(prompt: str, hide_input: bool = True):
    global _CLICK_VERSION
    kwargs = {}

    if _CLICK_VERSION is None:
        try:
            _CLICK_VERSION = parse_version(importlib_metadata.version("click"))
        except Exception:
            _CLICK_VERSION = parse_version("0.0.0")

    if _CLICK_VERSION.major >= 8:
        kwargs = {"prompt": prompt, "hide_input": hide_input, "prompt_required": False}

    return kwargs


def select_cluster(cluster: Optional[str] = None) -> str:
    """
    Retrieve available clusters and either return the specified one after validation
    or allow the user to interactively select from the list.
    """
    from truefoundry.deploy.lib.clients.servicefoundry_client import (
        ServiceFoundryServiceClient,
    )

    clusters = ServiceFoundryServiceClient().list_clusters()

    if not clusters:
        raise click.ClickException("No clusters found in your account.")

    if cluster:
        if not any(c.id == cluster for c in clusters):
            raise click.ClickException(
                f"Cluster {cluster} not found. Either it does not exist or you might not be authorized to access it"
            )
        return cluster

    choices = {cluster.id: cluster for cluster in clusters}
    selected_cluster = questionary.select(
        "Pick a Cluster:", choices=list(choices.keys())
    ).ask()
    if not selected_cluster:
        raise click.ClickException("No cluster selected.")
    return selected_cluster
