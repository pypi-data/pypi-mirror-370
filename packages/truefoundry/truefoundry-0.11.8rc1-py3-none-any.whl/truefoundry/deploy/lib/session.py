import os
from typing import Optional

import rich_click as click

from truefoundry.common.auth_service_client import AuthServiceClient
from truefoundry.common.constants import TFY_API_KEY_ENV_KEY, TFY_HOST_ENV_KEY
from truefoundry.common.credential_file_manager import CredentialsFileManager
from truefoundry.common.credential_provider import EnvCredentialProvider
from truefoundry.common.entities import CredentialsFileContent, Token
from truefoundry.common.session import Session
from truefoundry.common.utils import relogin_error_message, resolve_tfy_host
from truefoundry.deploy.io.output_callback import OutputCallBack
from truefoundry.deploy.lib.const import (
    RICH_OUTPUT_CALLBACK,
)
from truefoundry.deploy.lib.messages import (
    PROMPT_ALREADY_LOGGED_OUT,
    PROMPT_LOGOUT_SUCCESSFUL,
)
from truefoundry.logger import logger


def login(
    api_key: Optional[str] = None,
    host: Optional[str] = None,
    relogin: bool = False,
    output_hook: OutputCallBack = RICH_OUTPUT_CALLBACK,
) -> bool:
    if TFY_API_KEY_ENV_KEY in os.environ and TFY_HOST_ENV_KEY in os.environ:
        logger.warning(
            "Skipping login because environment variables %s and "
            "%s are set and will be used when running truefoundry. "
            "If you want to relogin then unset these environment keys.",
            TFY_HOST_ENV_KEY,
            TFY_API_KEY_ENV_KEY,
        )
        return False

    if EnvCredentialProvider.can_provide():
        logger.warning(
            "TFY_API_KEY env var is already set. "
            "When running truefoundry, it will use the api key to authorize.\n"
            "Login will just save the credentials on disk."
        )

    host = resolve_tfy_host(host)

    with CredentialsFileManager() as cred_file:
        if not relogin and cred_file.exists():
            cred_file_content = cred_file.read()
            if host != cred_file_content.host:
                if click.confirm(
                    f"Already logged in to {cred_file_content.host!r}\n"
                    f"Do you want to relogin to {host!r}?"
                ):
                    return login(api_key=api_key, host=host, relogin=True)

            user_info = cred_file_content.to_token().to_user_info()
            output_hook.print_line(
                relogin_error_message(
                    f"Already logged in to {cred_file_content.host!r} as {user_info.user_id!r}",
                    host=host,
                )
            )
            return False

        if api_key:
            token = Token(access_token=api_key, refresh_token=None)
        else:
            auth_service = AuthServiceClient.from_tfy_host(tfy_host=host)
            # interactive login
            token = _login_with_device_code(
                base_url=host, auth_service=auth_service, output_hook=output_hook
            )

        cred_file_content = CredentialsFileContent(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            host=host,
        )
        cred_file.write(cred_file_content)

    user_info = token.to_user_info()
    output_hook.print_line(
        f"Successfully logged in to {cred_file_content.host!r} as {user_info.user_id!r}"
    )
    return True


def logout(
    output_hook: OutputCallBack = RICH_OUTPUT_CALLBACK,
) -> None:
    with CredentialsFileManager() as cred_file:
        if cred_file.delete():
            output_hook.print_line(PROMPT_LOGOUT_SUCCESSFUL)
        else:
            output_hook.print_line(PROMPT_ALREADY_LOGGED_OUT)


def get_access_token():
    # Get the access token from the session
    session = Session.new()
    return session.access_token


def _login_with_device_code(
    base_url: str,
    auth_service: AuthServiceClient,
    output_hook: OutputCallBack = RICH_OUTPUT_CALLBACK,
) -> Token:
    logger.debug("Logging in with device code")
    device_code = auth_service.get_device_code()
    auto_open_url = None
    message = "Please click on the above link if it is not automatically opened in a browser window."
    if device_code.complete_verification_url:
        auto_open_url = device_code.complete_verification_url
    elif device_code.verification_url:
        if device_code.message:
            message = device_code.message
        else:
            message = (
                f"Please open the following URL in a browser and enter the code {device_code.user_code} "
                f"when prompted: {device_code.verification_url}"
            )
    else:
        auto_open_url = device_code.get_user_clickable_url(auth_host=base_url)
    if auto_open_url:
        output_hook.print_line(f"Opening:- {auto_open_url}")
        click.launch(auto_open_url)
    output_hook.print_line(message)
    return auth_service.get_token_from_device_code(
        device_code=device_code.device_code,
        timeout=device_code.expires_in_seconds,
        poll_interval_seconds=device_code.interval_in_seconds,
    )
