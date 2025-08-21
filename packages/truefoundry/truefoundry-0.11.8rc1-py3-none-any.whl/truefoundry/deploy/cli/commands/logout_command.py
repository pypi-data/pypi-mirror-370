import rich_click as click

from truefoundry.cli.const import COMMAND_CLS
from truefoundry.cli.util import handle_exception_wrapper
from truefoundry.deploy.io.rich_output_callback import RichOutputCallBack
from truefoundry.deploy.lib.session import logout


@click.command(name="logout", cls=COMMAND_CLS)
@handle_exception_wrapper
def logout_command():
    """
    Logout from current TrueFoundry session
    """
    callback = RichOutputCallBack()
    logout(output_hook=callback)


def get_logout_command():
    return logout_command
