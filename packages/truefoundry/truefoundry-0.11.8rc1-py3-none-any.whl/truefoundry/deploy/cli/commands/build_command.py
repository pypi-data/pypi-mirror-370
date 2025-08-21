import json

import rich_click as click

from truefoundry.cli.console import console
from truefoundry.cli.const import GROUP_CLS
from truefoundry.cli.util import handle_exception_wrapper
from truefoundry.deploy import builder
from truefoundry.version import __version__


@click.group(
    name="build",
    cls=GROUP_CLS,
    invoke_without_command=True,
    help="Build docker image locally from TrueFoundry spec",
    context_settings={"ignore_unknown_options": True, "allow_interspersed_args": True},
)
@click.option(
    "--name",
    type=click.STRING,
    required=True,
    help="Name for the image being build - used as docker tag",
)
@click.option(
    "--build-config",
    "--build_config",
    type=click.STRING,
    required=True,
    help="Build part of the spec as a json spec",
)
@click.argument("extra_opts", nargs=-1, type=click.UNPROCESSED)
@handle_exception_wrapper
def build_command(name, build_config, extra_opts):
    if build_config:
        console.print(rf"\[build] TrueFoundry CLI version: {__version__}")
        builder.build(
            build_configuration=json.loads(build_config),
            tag=name,
            extra_opts=extra_opts,
        )


def get_build_command():
    return build_command
