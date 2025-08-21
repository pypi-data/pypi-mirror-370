from typing import Any, Callable, Optional, Union

from flytekit import PythonFunctionTask
from flytekit.core.task import FuncOut, T
from flytekit.core.task import task as flytekit_task

from truefoundry.workflow import PythonTaskConfig


def task(
    _task_function: Optional[Callable[..., Any]] = None,
    task_config: Optional[PythonTaskConfig] = None,
    retries: Optional[int] = 0,
) -> Union[
    Callable[[Callable[..., FuncOut]], PythonFunctionTask[T]],
    PythonFunctionTask[T],
    Callable[..., FuncOut],
]:
    """
    This is the decorator used to run flyte tasks in TrueFoundry.

    Tasks are the building blocks of workflow. They represent users code. Tasks have the following properties

    * Versioned (usually tied to the git revision SHA1)
    * Strong interfaces (specified inputs and outputs)
    * Declarative
    * Independently executable
    * Unit testable

    For a simple python task,

    .. code-block:: python
        from truefoundry.workflow import task
        @task
        def my_task(x: int, y: typing.Dict[str, str]) -> str:
            ...

    For specific task types

    .. code-block:: python
        from truefoundry.workflow import task, PythonTaskConfig
        @task(task_config=PythonTaskConfig(), retries=2)
        def my_task(x: int, y: typing.Dict[str, str]) -> str:
            ...

    :param _task_function: The function to be wrapped as a task. This is optional and can be used as a decorator.
    :param task_config: The configuration for the task of class PythonTaskConfig. This is optional and defaults to an empty configuration.
    :param retries: The number of retries for the task. This is optional and defaults to 0.
    """
    return flytekit_task(_task_function, task_config=task_config, retries=retries)
