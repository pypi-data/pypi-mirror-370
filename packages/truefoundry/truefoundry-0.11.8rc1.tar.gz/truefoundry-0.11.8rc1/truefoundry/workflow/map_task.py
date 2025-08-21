from typing import Optional, cast

from flytekit import PythonFunctionTask
from flytekit.core.array_node_map_task import ArrayNodeMapTask

from truefoundry.workflow.task import PythonTaskConfig


class TrueFoundryArrayNodeMapTask(ArrayNodeMapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_custom(self, settings) -> dict:
        arraynode_custom_params = super().get_custom(settings)
        task_config = cast(PythonTaskConfig, self.python_function_task.task_config)
        return {
            "truefoundry": task_config.dict(),
            **arraynode_custom_params,
        }


def map_task(
    task_function: PythonFunctionTask,
    concurrency: Optional[int] = None,
    # TODO why no min_successes?
    min_success_ratio: float = 1.0,
    **kwargs,
):
    """Map task that uses the ``ArrayNode`` construct..

    .. important::

       This is an experimental drop-in replacement for :py:func:`~flytekit.map_task`.

    :param task_function: This argument is implicitly passed and represents the repeatable function
    :param concurrency: If specified, this limits the number of mapped tasks than can run in parallel to the given batch
        size. If the size of the input exceeds the concurrency value, then multiple batches will be run serially until
        all inputs are processed. If set to 0, this means unbounded concurrency. If left unspecified, this means the
        array node will inherit parallelism from the workflow
    :param min_success_ratio: If specified, this determines the minimum fraction of total jobs which can complete
        successfully before terminating this task and marking it successful.
    """
    return TrueFoundryArrayNodeMapTask(
        task_function,
        concurrency=concurrency,
        min_success_ratio=min_success_ratio,
        **kwargs,
    )
