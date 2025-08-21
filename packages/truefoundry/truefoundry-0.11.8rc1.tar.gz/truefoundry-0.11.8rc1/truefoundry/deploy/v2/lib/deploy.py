import sys
import time
from typing import Optional, TypeVar

import socketio
from rich.status import Status

from truefoundry.common.utils import poll_for_function
from truefoundry.deploy._autogen import models as autogen_models
from truefoundry.deploy.builder.docker_service import env_has_docker
from truefoundry.deploy.lib.clients.servicefoundry_client import (
    ServiceFoundryServiceClient,
)
from truefoundry.deploy.lib.dao.workspace import get_workspace_by_fqn
from truefoundry.deploy.lib.model.entity import Deployment, DeploymentTransitionStatus
from truefoundry.deploy.lib.util import get_application_fqn_from_deployment_fqn
from truefoundry.deploy.v2.lib.models import BuildResponse
from truefoundry.deploy.v2.lib.source import (
    local_source_to_image,
    local_source_to_remote_source,
)
from truefoundry.logger import logger
from truefoundry.pydantic_v1 import BaseModel

Component = TypeVar("Component", bound=BaseModel)


def _set_python_version_if_missing(build_spec: autogen_models.PythonBuild) -> None:
    if build_spec.python_version is None:
        client = ServiceFoundryServiceClient()
        server_default_python_version = (
            client.python_sdk_config.python_build_default_image_tag
        )
        logger.warning(
            f"No python version was provided in the spec, "
            f"using the default python version ({server_default_python_version}) from the server."
        )
        build_spec.python_version = server_default_python_version


def _handle_if_local_source(component: Component, workspace_fqn: str) -> Component:
    if (
        hasattr(component, "image")
        and isinstance(component.image, autogen_models.Build)
        and isinstance(component.image.build_source, autogen_models.LocalSource)
    ):
        new_component = component.copy(deep=True)

        if new_component.image.build_source.local_build:
            if not env_has_docker():
                logger.warning(
                    "Did not find Docker locally installed on this system, image will be built remotely. "
                    "For faster builds it is recommended to install Docker locally. "
                    "If you always want to build remotely, "
                    "please set `image.build_source.local_build` to `false` in your YAML spec or equivalently set "
                    "`image=Build(build_source=LocalSource(local_build=False, ...))` in your "
                    "`Service` or `Job` definition code."
                )
                local_build = False
            else:
                logger.info(
                    "Found locally installed docker, image will be built locally and then pushed.\n"
                    "If you want to always build remotely instead of locally, "
                    "please set `image.build_source.local_build` to `false` in your YAML spec or equivalently set "
                    "`image=Build(build_source=LocalSource(local_build=False, ...))` in your "
                    "`Service` or `Job` definition code."
                )
                local_build = True
        else:
            logger.info(
                "Image will be built remotely because `image.build_source.local_build` is set to `false`. "
                "For faster builds it is recommended to install Docker locally and "
                "set `image.build_source.local_build` to `true` in your YAML spec "
                "or equivalently set `image=Build(build_source=LocalSource(local_build=True, ...))` "
                "in your `Service` or `Job` definition code."
            )
            local_build = False

        if local_build:
            if isinstance(new_component.image.build_spec, autogen_models.PythonBuild):
                _set_python_version_if_missing(new_component.image.build_spec)
            # We are to build the image locally, push and update `image` in spec
            logger.info(
                "Building image for %s '%s'", new_component.type, new_component.name
            )
            new_component.image = local_source_to_image(
                build=new_component.image,
                docker_registry_fqn=new_component.image.docker_registry,
                workspace_fqn=workspace_fqn,
                component_name=new_component.name,
            )
        else:
            # We'll build image on TrueFoundry servers, upload the source and update image.build_source
            logger.info(
                "Uploading code for %s '%s'", new_component.type, new_component.name
            )
            client = ServiceFoundryServiceClient()
            new_component.image.build_source = local_source_to_remote_source(
                local_source=new_component.image.build_source,
                workspace_fqn=workspace_fqn,
                component_name=new_component.name,
                upload_code_package=client.upload_code_package,
            )
            logger.debug(
                "Uploaded code for %s '%s'", new_component.type, new_component.name
            )
        return new_component
    return component


def _log_application_dashboard_url(deployment: Deployment, log_message: str):
    application_id = deployment.applicationId

    # TODO: is there any simpler way to get this? :cry
    client = ServiceFoundryServiceClient()

    url = f"{client.tfy_host.strip('/')}/applications/{application_id}?tab=deployments"
    logger.info(log_message, url)


def _tail_build_logs(build_response: BuildResponse) -> socketio.Client:
    client = ServiceFoundryServiceClient()

    logger.info("Tailing build logs for '%s'", build_response.componentName)
    socket = client.tail_build_logs(build_response=build_response)
    return socket


def _deploy_wait_handler(  # noqa: C901
    deployment: Deployment,
    tail_logs: bool = True,
) -> Optional[DeploymentTransitionStatus]:
    tail_logs_or_polling_status_message = (
        "You can press Ctrl + C to exit the tailing of build logs "
    )
    if not tail_logs:
        tail_logs_or_polling_status_message = (
            "you can press Ctrl + C to exit the polling of deployment status "
        )
    _log_application_dashboard_url(
        deployment=deployment,
        log_message=(
            "You can track the progress below or on the dashboard:- '%s'\n"
            f"{tail_logs_or_polling_status_message}"
            "and deployment will continue on the server"
        ),
    )
    with Status(status="Polling for deployment status") as spinner:
        last_status_printed = None
        client = ServiceFoundryServiceClient()
        start_time = time.monotonic()
        total_timeout_time: int = 600
        poll_interval_seconds = 5
        time_elapsed = 0
        socket: socketio.Client = None

        for deployment_statuses in poll_for_function(
            client.get_deployment_statuses,
            poll_after_secs=poll_interval_seconds,
            application_id=deployment.applicationId,
            deployment_id=deployment.id,
            retry_count=10,
        ):
            if len(deployment_statuses) == 0:
                logger.warning("Did not receive any deployment status")
                continue

            latest_deployment_status = deployment_statuses[-1]

            status_to_print = (
                latest_deployment_status.transition or latest_deployment_status.status
            )
            spinner.update(status=f"Current state: {status_to_print}")
            if status_to_print != last_status_printed:
                if DeploymentTransitionStatus.is_failure_state(status_to_print):
                    logger.error("State: %r", status_to_print)
                else:
                    logger.info("State: %r", status_to_print)
                last_status_printed = status_to_print

            if latest_deployment_status.state.isTerminalState:
                if socket and socket.connected:
                    socket.disconnect()
                break

            if (
                latest_deployment_status.transition
                == DeploymentTransitionStatus.BUILDING
            ):
                if tail_logs and not socket:
                    try:
                        build_responses = client.get_deployment_build_response(
                            application_id=deployment.applicationId,
                            deployment_id=deployment.id,
                        )
                        socket = _tail_build_logs(build_responses[0])
                    except Exception as e:
                        logger.error("Error tailing build logs: %s", e)

            time_elapsed = time.monotonic() - start_time
            if time_elapsed > total_timeout_time:
                logger.warning(
                    "Polled build logs for %s secs. Disconnecting from server, the deployment will still continue.",
                    int(time_elapsed),
                )
                if socket and socket.connected:
                    socket.disconnect()
                break

    return last_status_printed


def _resolve_workspace_fqn(
    component: Component, workspace_fqn: Optional[str] = None
) -> str:
    if not workspace_fqn:
        if hasattr(component, "workspace_fqn") and component.workspace_fqn:
            resolved_workspace_fqn = component.workspace_fqn
        else:
            raise ValueError(
                f"""\
No Workspace FQN was provided or mentioned in the spec.
Either add a `workspace_fqn` to your yaml spec as

```
name: {getattr(component, "name", "my-app")}
type: {getattr(component, "type", "undefined")}
...
workspace_fqn: <your workspace fqn>
```

or Python deployment spec as

```
app = {component.__class__.__name__}(
    name='{getattr(component, "name", "my-app")}',
    ...
    workspace_fqn='<your workspace fqn>'
)
```

or pass it explicitly using `--workspace-fqn` argument on CLI.
"""
            )
    else:
        if (
            hasattr(component, "workspace_fqn")
            and component.workspace_fqn
            and component.workspace_fqn != workspace_fqn
        ):
            logger.warning(
                f"`workspace_fqn` set in the deployment spec doesn't match the provided `workspace_fqn` argument {component.workspace_fqn!r} \n"
                f"Using `workspace_fqn`: {workspace_fqn!r} "
            )
        resolved_workspace_fqn = workspace_fqn

    return resolved_workspace_fqn


def deploy_component(
    component: Component,
    workspace_fqn: Optional[str] = None,
    wait: bool = True,
    force: bool = False,
    trigger_on_deploy: bool = False,
) -> Deployment:
    workspace_fqn = _resolve_workspace_fqn(
        component=component, workspace_fqn=workspace_fqn
    )
    component.workspace_fqn = workspace_fqn
    workspace_id = get_workspace_by_fqn(workspace_fqn).id
    if isinstance(component, autogen_models.ApplicationSet):
        updated_component = component.copy(deep=True)
        if updated_component.components:
            for i, subcomponent in enumerate(updated_component.components):
                updated_component.components[i] = _handle_if_local_source(
                    component=subcomponent, workspace_fqn=workspace_fqn
                )
    else:
        updated_component = _handle_if_local_source(
            component=component, workspace_fqn=workspace_fqn
        )
    client = ServiceFoundryServiceClient()
    response = client.deploy_application(
        workspace_id=workspace_id,
        application=updated_component,
        force=force,
        trigger_on_deploy=trigger_on_deploy,
    )
    logger.info(
        "🚀 Deployment started for application '%s'. Deployment FQN is '%s'.",
        updated_component.name,
        response.fqn,
    )
    if wait:
        try:
            last_status_printed = _deploy_wait_handler(deployment=response)
            if not last_status_printed or DeploymentTransitionStatus.is_failure_state(
                last_status_printed
            ):
                deployment_tab_url = f"{client.tfy_host.strip('/')}/applications/{response.applicationId}?tab=deployments"
                message = f"Deployment Failed. Please refer to the logs for additional details - {deployment_tab_url}"
                sys.exit(message)
        except KeyboardInterrupt:
            logger.info("Ctrl-c executed. The deployment will still continue.")

    deployment_fqn = response.fqn
    application_fqn = get_application_fqn_from_deployment_fqn(deployment_fqn)
    logger.info("Deployment FQN: %s", deployment_fqn)
    logger.info("Application FQN: %s", application_fqn)

    _log_application_dashboard_url(
        deployment=response,
        log_message="You can find the application on the dashboard:- '%s'",
    )
    return response
