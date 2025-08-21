import logging
import sys

import rich_click as click

from truefoundry import logger
from truefoundry._ask.cli import get_ask_command
from truefoundry.cli.config import CliConfig
from truefoundry.cli.const import GROUP_CLS
from truefoundry.cli.util import setup_rich_click
from truefoundry.common.constants import TFY_DEBUG_ENV_KEY
from truefoundry.common.utils import is_internal_env_set
from truefoundry.deploy.cli.commands import (
    get_apply_command,
    get_build_command,
    get_delete_command,
    get_deploy_command,
    get_deploy_init_command,
    get_get_command,
    get_login_command,
    get_logout_command,
    get_patch_application_command,
    get_patch_command,
    get_terminate_command,
    get_trigger_command,
)
from truefoundry.ml.cli.cli import get_ml_cli
from truefoundry.version import __version__

click.rich_click.USE_RICH_MARKUP = True

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])  # noqa: C408


@click.group(
    cls=GROUP_CLS, context_settings=CONTEXT_SETTINGS, invoke_without_command=True
)
@click.option(
    "--json",
    is_flag=True,
    type=click.BOOL,
    help="Output entities in json format instead of formatted tables",
)
@click.option(
    "--debug",
    is_flag=True,
    type=click.BOOL,
    envvar=TFY_DEBUG_ENV_KEY,
    show_envvar=True,
    show_default=True,
    help="Set logging level to Debug. Can also be set using environment variable. E.g. TFY_DEBUG=1",
)
@click.version_option(
    version=__version__, message="TrueFoundry CLI: version %(version)s"
)
@click.pass_context
def truefoundry_cli(ctx, json, debug):
    """
    TrueFoundry provides an easy way to deploy your Services, Jobs and Models.
    \b

    To start, login to your TrueFoundry account with [code]tfy login[/]

    Then start deploying with [code]tfy deploy[/]

    Ask questions and troubleshoot your clusters with [code]tfy ask[/]

    And more: [link=https://docs.truefoundry.com/docs]https://docs.truefoundry.com/docs[/]

    """
    setup_rich_click()
    CliConfig.json = json
    CliConfig.debug = debug
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
    log_level = logging.INFO
    # no info logs while outputting json
    if json:
        log_level = logging.ERROR
    if debug:
        log_level = logging.DEBUG
    logger.add_cli_handler(level=log_level)


def create_truefoundry_cli() -> click.Group:
    """Generates CLI by combining all subcommands into a main CLI and returns in

    Returns:
        function: main CLI functions will all added sub-commands
    """
    cli = truefoundry_cli
    cli.add_command(get_login_command())
    cli.add_command(get_logout_command())
    cli.add_command(get_apply_command())
    cli.add_command(get_deploy_command())
    cli.add_command(get_deploy_init_command())
    cli.add_command(get_patch_application_command())
    cli.add_command(get_delete_command())
    cli.add_command(get_trigger_command())
    cli.add_command(get_terminate_command())
    cli.add_command(get_ml_cli())
    cli.add_command(get_get_command())
    cli.add_command(get_ask_command())

    if not (sys.platform.startswith("win32") or sys.platform.startswith("cygwin")):
        cli.add_command(get_patch_command())

    if is_internal_env_set():
        cli.add_command(get_build_command())
    return cli


def main():
    try:
        # We try and import readline to enable better prompt editing in the CLI
        import readline  # noqa: F401
    except ImportError:
        pass
    # Exit the interpreter by raising SystemExit(status).
    # If the status is omitted or None, it defaults to zero (i.e., success).
    # If the status is an integer, it will be used as the system exit status.
    # If it is another kind of object, it will be printed and the system exit status will be one (i.e., failure).
    try:
        cli = create_truefoundry_cli()
    except Exception as e:
        raise click.UsageError(message=str(e)) from e
    sys.exit(cli())


if __name__ == "__main__":
    main()
