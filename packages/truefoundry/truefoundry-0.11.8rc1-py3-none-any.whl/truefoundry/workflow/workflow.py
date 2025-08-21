from typing import Any, Callable, Dict, List, Optional, Union

from flytekit.core.base_task import Task
from flytekit.core.launch_plan import LaunchPlan
from flytekit.core.schedule import CronSchedule
from flytekit.core.workflow import (
    FuncOut,
    PythonFunctionWorkflow,
    WorkflowFailurePolicy,
)
from flytekit.core.workflow import workflow as flytekit_workflow

from truefoundry.deploy._autogen.models import WorkflowAlert
from truefoundry.pydantic_v1 import BaseModel

TRUEFOUNDRY_LAUNCH_PLAN_NAME = "default"
TRUEFOUNDRY_ALERTS_CONFIG = "tfy_alerts_config"


class ExecutionConfig(BaseModel):
    # I am not using job's Schedule here because:
    # 1. flyte accepts schedule only as a string
    # 2. flyte doesn't support setting concurrency policy
    schedule: str


class TruefoundryConfigStore(BaseModel):
    execution_config_map: Dict[str, ExecutionConfig] = {}

    def reset(self):
        self.execution_config_map = {}

    def get(self, key: str) -> Optional[ExecutionConfig]:
        return self.execution_config_map.get(key)

    def set(self, key: str, value: ExecutionConfig):
        self.execution_config_map[key] = value


truefoundry_config_store = TruefoundryConfigStore()


def workflow(
    _workflow_function: Optional[Callable[..., Any]] = None,
    failure_policy: Optional[WorkflowFailurePolicy] = None,
    on_failure: Optional[Task] = None,
    execution_configs: Optional[List[ExecutionConfig]] = None,
    alerts: Optional[List[WorkflowAlert]] = None,
) -> Union[
    Callable[[Callable[..., FuncOut]], PythonFunctionWorkflow],
    PythonFunctionWorkflow,
    Callable[..., FuncOut],
]:
    """
    This decorator declares a function to be a Flyte workflow. Workflows are declarative entities that construct a DAG
    of tasks using the data flow between tasks.

    Unlike a task, the function body of a workflow is evaluated at serialization-time (aka compile-time). This is
    because while we can determine the entire structure of a task by looking at the function's signature, workflows need
    to run through the function itself because the body of the function is what expresses the workflow structure. It's
    also important to note that, local execution notwithstanding, it is not evaluated again when the workflow runs on
    Flyte.
    That is, workflows should not call non-Flyte entities since they are only run once (again, this is with respect to
    the platform, local runs notwithstanding).

    Example:

    .. literalinclude:: ../../../tests/flytekit/unit/core/test_workflows.py
       :pyobject: my_wf_example

    Again, users should keep in mind that even though the body of the function looks like regular Python, it is
    actually not. When flytekit scans the workflow function, the objects being passed around between the tasks are not
    your typical Python values. So even though you may have a task ``t1() -> int``, when ``a = t1()`` is called, ``a``
    will not be an integer so if you try to ``range(a)`` you'll get an error.

    Please see the :ref:`user guide <cookbook:workflow>` for more usage examples.

    :param _workflow_function: This argument is implicitly passed and represents the decorated function.
    :param failure_policy: Use the options in flytekit.WorkflowFailurePolicy
    :param on_failure: Invoke this workflow or task on failure. The Workflow / task has to match the signature of
         the current workflow, with an additional parameter called `error` Error
    """
    if _workflow_function is None:

        def wrapper(func: Callable[..., Any]) -> Any:
            return workflow(
                _workflow_function=func,
                failure_policy=failure_policy,
                on_failure=on_failure,
                execution_configs=execution_configs,
                alerts=alerts,
            )

        return wrapper

    workflow_object = flytekit_workflow(
        _workflow_function,
        failure_policy=failure_policy,
        on_failure=on_failure,
    )
    execution_configs = execution_configs or []
    if len(execution_configs) > 1:
        raise ValueError("Only one cron execution config is allowed per workflow")

    if execution_configs:
        execution_config = execution_configs[0]
        # flyte maintains this in-memory and uses it while serialization
        LaunchPlan.get_or_create(
            workflow=workflow_object,
            name=TRUEFOUNDRY_LAUNCH_PLAN_NAME,
            schedule=CronSchedule(schedule=execution_config.schedule),
        )
        function_module = _workflow_function.__module__
        function_name = _workflow_function.__name__
        function_path = f"{function_module}.{function_name}"
        truefoundry_config_store.set(function_path, execution_config)

    if alerts:
        truefoundry_config_store.set(TRUEFOUNDRY_ALERTS_CONFIG, alerts)

    return workflow_object
