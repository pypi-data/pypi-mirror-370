from typing import Callable, Tuple, Union

from flytekit import FlyteContext, PythonFunctionTask
from flytekit.extend import Promise, TaskPlugins

from truefoundry.logger import logger
from truefoundry.workflow import PythonTaskConfig


class TrueFoundryFunctionTask(PythonFunctionTask[PythonTaskConfig]):
    # Note(nikp1172) We are not creating our task type for now, we just re-use their task type for now
    def __init__(
        self,
        task_config: PythonTaskConfig,
        task_function: Callable,
        **kwargs,
    ):
        super().__init__(task_config=task_config, task_function=task_function, **kwargs)

    def local_execute(
        self, ctx: FlyteContext, **kwargs
    ) -> Union[Tuple[Promise], Promise, None]:
        logger.warning(
            "Running pod task locally. Local environment may not match pod environment which may cause issues."
        )
        return super().local_execute(ctx=ctx, **kwargs)

    def get_custom(self, settings) -> dict:
        return {"truefoundry": self._task_config.dict()}


TaskPlugins.register_pythontask_plugin(PythonTaskConfig, TrueFoundryFunctionTask)
