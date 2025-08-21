from truefoundry.deploy.cli.commands.apply_command import get_apply_command
from truefoundry.deploy.cli.commands.build_command import get_build_command
from truefoundry.deploy.cli.commands.delete_command import get_delete_command
from truefoundry.deploy.cli.commands.deploy_command import get_deploy_command
from truefoundry.deploy.cli.commands.deploy_init_command import get_deploy_init_command
from truefoundry.deploy.cli.commands.get_command import get_get_command
from truefoundry.deploy.cli.commands.login_command import get_login_command
from truefoundry.deploy.cli.commands.logout_command import get_logout_command
from truefoundry.deploy.cli.commands.logs_command import get_logs_command
from truefoundry.deploy.cli.commands.patch_application_command import (
    get_patch_application_command,
)
from truefoundry.deploy.cli.commands.patch_command import get_patch_command
from truefoundry.deploy.cli.commands.terminate_comand import get_terminate_command
from truefoundry.deploy.cli.commands.trigger_command import get_trigger_command

__all__ = [
    "get_apply_command",
    "get_build_command",
    "get_delete_command",
    "get_deploy_command",
    "get_deploy_init_command",
    "get_get_command",
    "get_login_command",
    "get_logout_command",
    "get_logs_command",
    "get_patch_application_command",
    "get_patch_command",
    "get_terminate_command",
    "get_trigger_command",
]
