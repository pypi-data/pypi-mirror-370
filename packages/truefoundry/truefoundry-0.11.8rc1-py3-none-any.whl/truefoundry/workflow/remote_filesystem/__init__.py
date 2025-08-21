import logging

from truefoundry.common.constants import ENV_VARS
from truefoundry.workflow.remote_filesystem.logger import init_logger

init_logger(level=ENV_VARS.TFY_INTERNAL_SIGNED_URL_CLIENT_LOG_LEVEL)
