import asyncio
import logging
from typing import Callable, Dict, Optional, Tuple, Union

import rich_click as click
from openai import AsyncOpenAI
from rich.console import Console

from truefoundry.cli.config import CliConfig
from truefoundry.cli.const import COMMAND_CLS
from truefoundry.cli.util import handle_exception_wrapper, select_cluster
from truefoundry.common.constants import (
    ENV_VARS,
    TFY_ASK_MODEL_NAME_KEY,
    TFY_ASK_OPENAI_API_KEY_KEY,
    TFY_ASK_OPENAI_BASE_URL_KEY,
)
from truefoundry.common.session import Session
from truefoundry.common.utils import get_tfy_servers_config

console = Console()


class CustomAsyncOpenAI(AsyncOpenAI):
    def __init__(
        self, *, api_key: Optional[Union[str, Callable[[], str]]] = None, **kwargs
    ):
        self.__api_key_fn = None
        if isinstance(api_key, str) or api_key is None:
            _api_key = api_key
        else:
            self.__api_key_fn = api_key
            _api_key = self.__api_key_fn()
        super().__init__(api_key=_api_key, **kwargs)

    @property
    def auth_headers(self) -> Dict[str, str]:
        if self.__api_key_fn is not None:
            api_key = self.__api_key_fn()
        else:
            api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}


def _get_openai_client(session: Session) -> Tuple[CustomAsyncOpenAI, str]:
    """
    Returns an AsyncOpenAI client using either user-provided credentials or TrueFoundry LLM gateway.
    """
    if ENV_VARS.TFY_ASK_OPENAI_BASE_URL:
        console.print(
            f"Found custom OpenAI compatible API settings ([green]{TFY_ASK_OPENAI_BASE_URL_KEY}[/green]) in env"
        )
        if ENV_VARS.TFY_ASK_OPENAI_API_KEY:
            console.print(
                f"Found API key ([green]{TFY_ASK_OPENAI_API_KEY_KEY}[/green]) in env"
            )
            api_key = ENV_VARS.TFY_ASK_OPENAI_API_KEY
        else:
            console.print(
                f"No API key found in env, using [yellow]EMPTY[/yellow] as API key"
                f"\n[dim]Tip: To use a different API key, set the env var "
                f"[green]{TFY_ASK_OPENAI_API_KEY_KEY}[/green] to the API key you want to use.[/dim]"
            )
            api_key = "EMPTY"
        base_url = ENV_VARS.TFY_ASK_OPENAI_BASE_URL
        default_model = "gpt-4o"
    else:
        tfy_servers_config = get_tfy_servers_config(session.tfy_host)
        base_url = f"{tfy_servers_config.servicefoundry_server_url}/v1/tfy-ai/proxy/api/inference/openai"
        console.print(
            f"Using TrueFoundry Managed AI."
            f"\n[dim]Tip: To use your own OpenAI API compatible API for the ask command, set the following env vars"
            f"\n * [green]{TFY_ASK_OPENAI_BASE_URL_KEY}[/] to the base URL of your OpenAI compatible API. E.g. [yellow]https://api.openai.com/v1[/yellow]"
            f"\n * [green]{TFY_ASK_OPENAI_API_KEY_KEY}[/] to the API key of your OpenAI compatible API."
            f"[/dim]"
        )
        console.print("")

        api_key = lambda: session.access_token  # noqa: E731
        default_model = "tfy-ai-openai/gpt-4o"
    client = CustomAsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
    )
    if ENV_VARS.TFY_ASK_MODEL_NAME:
        openai_model = ENV_VARS.TFY_ASK_MODEL_NAME
        console.print(
            f"Using custom model from env [green]{TFY_ASK_MODEL_NAME_KEY}[/green]: [yellow]{openai_model}[/yellow]"
        )
    else:
        openai_model = default_model
        console.print(
            f"Using default model: [yellow]{openai_model}[/yellow]"
            f"\n[dim]Tip: To use a different model, set the env var "
            f"[green]{TFY_ASK_MODEL_NAME_KEY}[/green] to the model name you want to use.[/dim]"
        )
    console.print("")

    if ENV_VARS.TFY_ASK_OPENAI_BASE_URL:
        console.print(
            "[dim][yellow]This operation will use tokens from your model provider and may incur costs.[/yellow][/dim]"
        )
        console.print("")
    return client, openai_model


@click.command(name="ask", cls=COMMAND_CLS)
@click.option(
    "-c",
    "--cluster",
    type=str,
    required=False,
    help="The cluster id from TrueFoundry. If not provided, an interactive prompt will list available clusters",
)
@click.pass_context
@handle_exception_wrapper
def ask_command(ctx, cluster: str) -> None:
    """
    Ask questions related to your Cluster in TrueFoundry.
    """
    from truefoundry._ask.client import ask_client

    debug = CliConfig.debug
    if debug:
        _mcp_logger = logging.getLogger("mcp")
        _mcp_logger.setLevel(logging.DEBUG)
        _mcp_logger.addHandler(logging.StreamHandler())

    session = Session.new()
    console.print(
        "\n[bold green]Welcome to the Ask Command![/bold green]\n"
        "Use this command to ask questions and troubleshoot issues in your Kubernetes cluster managed by the TrueFoundry Control Plane.\n"
        "It helps you investigate and identify potential problems across services, pods, deployments, and more.\n"
    )
    openai_client, openai_model = _get_openai_client(session=session)
    if not cluster:
        console.print(
            "[dim]Tip: You can specify a cluster using the '--cluster' option, or select one interactively from the list.[/dim]\n"
        )
    cluster = select_cluster(cluster)
    tfy_servers_config = get_tfy_servers_config(session.tfy_host)
    mcp_server_url = f"{tfy_servers_config.servicefoundry_server_url}/v1/k8s-mcp"
    asyncio.run(
        ask_client(
            cluster=cluster,
            server_url=mcp_server_url,
            token=session.access_token,
            openai_client=openai_client,
            openai_model=openai_model,
            debug=debug,
        )
    )


def get_ask_command():
    return ask_command
