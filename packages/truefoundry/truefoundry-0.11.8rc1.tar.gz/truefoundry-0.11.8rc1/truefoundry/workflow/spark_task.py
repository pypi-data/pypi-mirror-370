import os
import shutil
from typing import Any, Callable, Dict, Optional

from flytekit import FlyteContextManager, PythonFunctionTask, lazy_module
from flytekit.configuration import SerializationSettings
from flytekit.core.context_manager import ExecutionParameters
from flytekit.extend import ExecutionState, TaskPlugins
from flytekit.extend.backend.base_agent import AsyncAgentExecutorMixin

from truefoundry.deploy.v2.lib.patched_models import PySparkTaskConfig

pyspark_sql = lazy_module("pyspark.sql")
SparkSession = pyspark_sql.SparkSession


class TfySparkFunctionTask(
    AsyncAgentExecutorMixin, PythonFunctionTask[PySparkTaskConfig]
):
    """
    Actual Plugin that transforms the local python code for execution within a spark context
    """

    _SPARK_TASK_TYPE = "spark"

    def __init__(
        self,
        task_config: PySparkTaskConfig,
        task_function: Callable,
        **kwargs,
    ):
        self.sess: Optional[SparkSession] = None  # type: ignore

        task_type = self._SPARK_TASK_TYPE

        super(TfySparkFunctionTask, self).__init__(
            task_config=task_config,
            task_type=task_type,
            task_function=task_function,
            **kwargs,
        )

    def get_custom(self, settings: SerializationSettings) -> Dict[str, Any]:
        return {"truefoundry": self._task_config.dict()}

    def pre_execute(self, user_params: ExecutionParameters) -> ExecutionParameters:
        import pyspark as _pyspark

        ctx = FlyteContextManager.current_context()
        sess_builder = _pyspark.sql.SparkSession.builder.appName(
            f"FlyteSpark: {user_params.execution_id}"
        )
        if not (
            ctx.execution_state
            and ctx.execution_state.mode == ExecutionState.Mode.TASK_EXECUTION
        ):
            # If either of above cases is not true, then we are in local execution of this task
            # Add system spark-conf for local/notebook based execution.
            spark_conf = _pyspark.SparkConf()
            spark_conf.set("spark.driver.bindAddress", "127.0.0.1")
            for k, v in self.task_config.spark_conf.items():
                spark_conf.set(k, v)
            # In local execution, propagate PYTHONPATH to executors too. This makes the spark
            # execution hermetic to the execution environment. For example, it allows running
            # Spark applications using Bazel, without major changes.
            if "PYTHONPATH" in os.environ:
                spark_conf.setExecutorEnv("PYTHONPATH", os.environ["PYTHONPATH"])
            sess_builder = sess_builder.config(conf=spark_conf)

        self.sess = sess_builder.getOrCreate()

        if (
            ctx.serialization_settings
            and ctx.serialization_settings.fast_serialization_settings
            and ctx.serialization_settings.fast_serialization_settings.enabled
            and ctx.execution_state
            and ctx.execution_state.mode == ExecutionState.Mode.TASK_EXECUTION
        ):
            file_name = "flyte_wf"
            file_format = "zip"
            shutil.make_archive(file_name, file_format, os.getcwd())
            self.sess.sparkContext.addPyFile(f"{file_name}.{file_format}")

        return user_params.builder().add_attr("SPARK_SESSION", self.sess).build()

    def execute(self, **kwargs) -> Any:
        return PythonFunctionTask.execute(self, **kwargs)


# Inject the Spark plugin into flytekits dynamic plugin loading system
TaskPlugins.register_pythontask_plugin(PySparkTaskConfig, TfySparkFunctionTask)
