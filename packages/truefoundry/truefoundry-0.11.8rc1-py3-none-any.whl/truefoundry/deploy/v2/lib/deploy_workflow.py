import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

import requirements
from flytekit.configuration import (
    SERIALIZED_CONTEXT_ENV_VAR,
    ImageConfig,
    SerializationSettings,
)
from flytekit.configuration import Image as FlytekitImage
from flytekit.models.launch_plan import LaunchPlan as FlyteLaunchPlan
from flytekit.tools.repo import (
    serialize_get_control_plane_entities as get_serialized_entities,
)
from flytekit.tools.repo import serialize_load_only as serialize_workflow
from flytekit.tools.translator import TaskSpec as FlyteTaskSpec
from flytekit.tools.translator import WorkflowSpec as FlyteWorkflowSpec
from google.protobuf.json_format import MessageToDict

from truefoundry.common.types import UploadCodePackageCallable
from truefoundry.deploy._autogen import models as autogen_models
from truefoundry.deploy.lib.clients.servicefoundry_client import (
    ServiceFoundryServiceClient,
)
from truefoundry.deploy.lib.dao.workspace import get_workspace_by_fqn
from truefoundry.deploy.lib.model.entity import Deployment, DeploymentTransitionStatus
from truefoundry.deploy.v2.lib.deploy import _deploy_wait_handler
from truefoundry.deploy.v2.lib.source import (
    local_source_to_remote_source,
)
from truefoundry.logger import logger
from truefoundry.pydantic_v1 import ValidationError
from truefoundry.workflow.workflow import (
    TRUEFOUNDRY_ALERTS_CONFIG,
    TRUEFOUNDRY_LAUNCH_PLAN_NAME,
    truefoundry_config_store,
)


def _handle_code_upload_for_workflow(
    workflow: autogen_models.Workflow,
    workspace_fqn: str,
    upload_code_package: UploadCodePackageCallable,
) -> autogen_models.Workflow:
    new_workflow = workflow.copy(deep=True)
    new_workflow.source = local_source_to_remote_source(
        local_source=workflow.source,
        workspace_fqn=workspace_fqn,
        component_name=workflow.name,
        upload_code_package=upload_code_package,
    )
    return new_workflow


def _is_tfy_workflow_package(package: requirements.parser.Requirement) -> bool:
    return package.name == "truefoundry" and "workflow" in package.extras


def _is_tfy_wf_present_in_pip_packages_or_requirements_file(
    pip_packages: List[str],
    project_root_path: str,
    requirements_path: Optional[str] = None,
) -> bool:
    for package in pip_packages:
        parsed_package = requirements.parser.Requirement.parse(package)
        if _is_tfy_workflow_package(parsed_package):
            return True
    if requirements_path:
        requirements_file_absolute_path = os.path.join(
            project_root_path, requirements_path
        )
        if not os.path.exists(requirements_file_absolute_path):
            raise FileNotFoundError(
                f"requirements file not found at {requirements_file_absolute_path}. requirements file path should be relative to project root path."
            )
        with open(requirements_file_absolute_path, "r") as file:
            for package in requirements.parse(file):
                if _is_tfy_workflow_package(package):
                    return True
    return False


def _is_tfy_wf_present_in_task_python_build(
    task_image_spec: Dict, project_root_path: str
) -> bool:
    pip_packages = task_image_spec["pip_packages"] or []
    requirements_path = task_image_spec.get("requirements_path")
    return _is_tfy_wf_present_in_pip_packages_or_requirements_file(
        pip_packages=pip_packages,
        project_root_path=project_root_path,
        requirements_path=requirements_path,
    )


def _is_dynamic_task(flyte_task: FlyteTaskSpec) -> bool:
    envs: Dict[str, str] = flyte_task.template.container.env or {}
    return SERIALIZED_CONTEXT_ENV_VAR in envs.keys()


# this function does validation that num_workflows = 1, this also validates task_config is passed correctly.
# This is verified by pydantic but doing it here also as error messages are not clear in pydantic
def _validate_workflow_entities(  # noqa: C901
    workflow_entities: List[Union[FlyteWorkflowSpec, FlyteLaunchPlan, FlyteTaskSpec]],
    project_root_path: str,
):
    workflow_objs: List[FlyteWorkflowSpec] = []
    launch_plans: List[FlyteLaunchPlan] = []
    tasks: List[FlyteTaskSpec] = []
    for entity in workflow_entities:
        if isinstance(entity, FlyteWorkflowSpec):
            workflow_objs.append(entity)
        elif isinstance(entity, FlyteLaunchPlan):
            launch_plans.append(entity)
        elif isinstance(entity, FlyteTaskSpec):
            tasks.append(entity)
        else:
            raise ValueError(f"Invalid entity found in workflow: {entity}")
    if len(workflow_objs) != 1:
        raise ValueError(
            f"Workflow file must have exactly one workflow object. Found {len(workflow_objs)}"
        )
    if len(launch_plans) > 2:
        raise ValueError(
            f"Workflow file must have exactly one launch plan. Found {len(launch_plans) - 1}"
        )

    error_message_to_use_truefoundry_decorators = """Invalid task definition for task: {}, Please use valid truefoundry decorator/class and pass task_config for tasks.
        You can import truefoundry task decorators using:
        `from truefoundry.workflow import task, ContainerTask, map_task`
        You can pass task config using `task_config` parameter in the task definition. Task config should be one of the following:
        `PythonTaskConfig`, or  `ContainerTaskConfig`. You can import these using:
        `from truefoundry.workflow import PythonTaskConfig, ContainerTaskConfig`
         """
    tasks_without_truefoundry_worflow_package = []
    task_names = set()
    for task in tasks:
        if _is_dynamic_task(task):
            raise ValueError("Dynamic workflows are not supported yet.")
        if not task.template.custom:
            raise ValueError(
                error_message_to_use_truefoundry_decorators.format(
                    task.template.id.name
                )
            )
        task_name = task.template.id.name
        if task_name in task_names:
            raise ValueError(
                f"Task name should be unique, task with name {task_name} is repeated in the workflow"
            )
        task_names.add(task_name)
        task_image_spec = task.template.custom["truefoundry"]["image"]
        if task_image_spec["type"] == "task-python-build":
            is_tfy_wf_present_in_task_python_build = (
                _is_tfy_wf_present_in_task_python_build(
                    task_image_spec=task_image_spec, project_root_path=project_root_path
                )
            )
            if not is_tfy_wf_present_in_task_python_build:
                tasks_without_truefoundry_worflow_package.append(task.template.id.name)
        try:
            autogen_models.FlyteTaskCustom.validate(task.template.custom)
        except ValidationError:
            raise ValueError(
                error_message_to_use_truefoundry_decorators.format(
                    task.template.id.name
                )
            ) from None
    if len(tasks_without_truefoundry_worflow_package) > 0:
        raise ValueError(
            rf"truefoundry\[workflow] package is required dependency to run workflows, add it in pip_packages for tasks: {', '.join(tasks_without_truefoundry_worflow_package)}"
        )

    # validate that all inputs have default values for cron workflows
    for launch_plan in launch_plans:
        if (
            truefoundry_config_store.get(launch_plan.spec.workflow_id.name)
            and launch_plan.id.name == TRUEFOUNDRY_LAUNCH_PLAN_NAME
        ):
            workflow_inputs = launch_plan.spec.default_inputs.parameters
            for input in workflow_inputs:
                if workflow_inputs[input].required:
                    raise ValueError(
                        f"All inputs must have default for a cron workflow. Input {input} is required in workflow but default value is not provided"
                    )


def _get_relative_package_path_from_filepath(
    project_root_path: str, filepath: str
) -> str:
    """
    This function returns the relative package path from the project root path for a given file path.
    e.g. if project_root_path = /home/user/project and filepath = /home/user/project/src/module.py
    then the function will return src.module
    """
    relative_file_path = os.path.relpath(filepath, project_root_path)
    path = Path(relative_file_path)
    package_path = str(path.with_suffix("")).replace(os.path.sep, ".")

    return package_path


def _generate_manifest_for_workflow(
    workflow: autogen_models.Workflow,
):
    settings = SerializationSettings(
        # We are adding these defaults to avoid validation errors in flyte objects
        image_config=ImageConfig(default_image=FlytekitImage(name="", tag="", fqn="")),
        python_interpreter=sys.executable,
    )
    source_absolute_path = os.path.abspath(workflow.source.project_root_path)

    workflow_file_absolute_path = os.path.join(
        source_absolute_path, workflow.workflow_file_path
    )
    if not os.path.exists(workflow_file_absolute_path):
        raise FileNotFoundError(
            f"Workflow file not found at {workflow_file_absolute_path}. Workflow file path should be relative to project root path."
        )

    package_path = _get_relative_package_path_from_filepath(
        project_root_path=source_absolute_path, filepath=workflow_file_absolute_path
    )

    serialize_workflow(
        pkgs=[package_path], settings=settings, local_source_root=source_absolute_path
    )
    workflow_entities = get_serialized_entities(
        settings, local_source_root=source_absolute_path
    )
    _validate_workflow_entities(workflow_entities, source_absolute_path)

    workflow.flyte_entities = []
    for entity in workflow_entities:
        if isinstance(entity, FlyteLaunchPlan):
            workflow_name = entity.spec.workflow_id.name

            # this is the case when someone has a cron schedule. and this line is for handling default launch plan in this case.
            if (
                truefoundry_config_store.get(workflow_name)
                and workflow_name == entity.id.name
            ):
                continue
            # this is the case when someone does not have a cron schedule. and this line is for handling default launch plan in this case.
            elif entity.id.name == workflow_name:
                entity._id._name = TRUEFOUNDRY_LAUNCH_PLAN_NAME
            # this the case when some workflow doesn't have cron schedule, neither it is default launch plan
            elif entity.id.name != TRUEFOUNDRY_LAUNCH_PLAN_NAME:
                raise ValueError(
                    f"Creating launch plans is not allowed. Found launch plan with name {entity.id.name}"
                )
        message_dict = MessageToDict(entity.to_flyte_idl())
        # proto message to dict conversion converts all int to float. so we need this hack
        if (
            message_dict.get("template")
            and message_dict["template"].get("custom")
            and message_dict["template"]["custom"].get("truefoundry")
        ):
            parsed_model = autogen_models.FlyteTaskCustom.parse_obj(
                message_dict["template"]["custom"]
            )
            message_dict["template"]["custom"]["truefoundry"] = parsed_model.truefoundry

        workflow.flyte_entities.append(message_dict)

    alerts_config = truefoundry_config_store.get(TRUEFOUNDRY_ALERTS_CONFIG)
    if alerts_config:
        if not workflow.alerts:
            workflow.alerts = alerts_config
        else:
            logger.warning(
                "Alerts are configured in both workflow decorator as well as in deployment config. Alerts configured in workflow decorator will be ignored."
            )
    # this step is just to verify if pydantic model is still valid after adding flyte_entities
    autogen_models.Workflow.validate({**workflow.dict()})


def _validate_workspace_fqn(
    workflow: autogen_models.Workflow,
    workspace_fqn: Optional[str] = None,
):
    if not workspace_fqn:
        raise ValueError(
            "No Workspace FQN was provided. "
            "Pass it explicitly using `--workspace-fqn` argument on CLI or `workspace_fqn` argument of `deploy_workflow`."
        )


def deploy_workflow(
    workflow: autogen_models.Workflow,
    workspace_fqn: str,
    wait: bool = True,
    force: bool = False,
) -> Deployment:
    _generate_manifest_for_workflow(workflow)
    _validate_workspace_fqn(workflow, workspace_fqn)

    # we need to rest the execution config store as it is a global variable and we don't want to keep the cron execution config for next workflow
    # this is only needed for notebook environment
    truefoundry_config_store.reset()

    workspace_id = get_workspace_by_fqn(workspace_fqn).id

    logger.info(
        f"Deploying workflow {workflow.name} to workspace {workspace_fqn} ({workspace_id})"
    )
    client = ServiceFoundryServiceClient()

    workflow = _handle_code_upload_for_workflow(
        workflow=workflow,
        workspace_fqn=workspace_fqn,
        upload_code_package=client.upload_code_package,
    )

    deployment = client.deploy_application(
        workspace_id=workspace_id,
        application=workflow,
        force=force,
    )
    logger.info(
        "🚀 Deployment started for application '%s'. Deployment FQN is '%s'.",
        workflow.name,
        deployment.fqn,
    )
    deployment_url = f"{client.tfy_host.strip('/')}/applications/{deployment.applicationId}?tab=deployments"
    if wait:
        try:
            last_status_printed = _deploy_wait_handler(
                deployment=deployment, tail_logs=False
            )
            if not last_status_printed or DeploymentTransitionStatus.is_failure_state(
                last_status_printed
            ):
                deployment_tab_url = f"{client.tfy_host.strip('/')}/applications/{deployment.applicationId}?tab=deployments"
                message = f"Deployment Failed. Please refer to the logs for additional details - {deployment_tab_url}"
                sys.exit(message)
        except KeyboardInterrupt:
            logger.info("Ctrl-c executed. The deployment will still continue.")
    logger.info("You can find the application on the dashboard:- '%s'", deployment_url)
