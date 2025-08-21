import rich_click as click

from truefoundry.cli.const import COMMAND_CLS
from truefoundry.cli.util import (
    handle_exception_wrapper,
    prompt_if_no_value_and_supported,
)
from truefoundry.common.constants import TFY_HOST_ENV_KEY
from truefoundry.deploy.io.rich_output_callback import RichOutputCallBack
from truefoundry.deploy.lib.session import login


@click.command(name="login", cls=COMMAND_CLS)
@click.option("--relogin", type=click.BOOL, is_flag=True, default=False)
@click.option(
    "--host",
    type=click.STRING,
    required=True,
    envvar=TFY_HOST_ENV_KEY,
    show_envvar=True,
)
@click.option(
    "--api-key",
    "--api_key",
    type=click.STRING,
    default=None,
    **prompt_if_no_value_and_supported(prompt="API Key", hide_input=True),
)
@handle_exception_wrapper
def login_command(relogin: bool, host: str, api_key: str):
    """
    Login to TrueFoundry
    """
    callback = RichOutputCallBack()
    login(api_key=api_key, host=host, relogin=relogin, output_hook=callback)


def get_login_command():
    return login_command
