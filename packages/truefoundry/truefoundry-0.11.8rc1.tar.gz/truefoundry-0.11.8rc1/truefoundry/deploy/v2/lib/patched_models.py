import enum
import os
import re
import warnings
from typing import Literal, Optional, Union

from truefoundry.common.warnings import TrueFoundryDeprecationWarning
from truefoundry.deploy._autogen import models
from truefoundry.pydantic_v1 import (
    BaseModel,
    Field,
    constr,
    root_validator,
    validator,
)

AUTO_DISCOVERED_REQUIREMENTS_TXT_WARNING_MESSAGE_TEMPLATE = """\
Using automatically discovered {requirements_txt_path} as the requirements file.
This auto discovery behavior is deprecated and will be removed in a future release.
Please specify the relative path of requirements file explicitly as

```python
build=Build(
    ...
    build_spec=PythonBuild(
        ...
        requirements_path={requirements_txt_path!r}
    )
)
```

OR

```yaml
build:
  type: build
  build_spec:
    type: tfy-python-buildpack
    requirements_path: {requirements_txt_path!r}
    ...
...
```

or set it to None if you don't want use any requirements file.
"""


def _resolve_requirements_path(
    build_context_path: str,
    requirements_path: Optional[str],
) -> Optional[str]:
    if requirements_path:
        return requirements_path

    # TODO: Deprecated behavior, phase out auto discovery in future release
    possible_requirements_txt_filename = "requirements.txt"
    possible_requirements_txt_path = os.path.join(
        build_context_path, possible_requirements_txt_filename
    )

    if os.path.isfile(possible_requirements_txt_path):
        requirements_txt_path = os.path.relpath(
            possible_requirements_txt_path, start=build_context_path
        )
        warnings.warn(
            AUTO_DISCOVERED_REQUIREMENTS_TXT_WARNING_MESSAGE_TEMPLATE.format(
                requirements_txt_path=requirements_txt_path
            ),
            category=TrueFoundryDeprecationWarning,
            stacklevel=2,
        )
        return requirements_txt_path

    return None


class CUDAVersion(str, enum.Enum):
    CUDA_11_0_CUDNN8 = "11.0-cudnn8"
    CUDA_11_1_CUDNN8 = "11.1-cudnn8"
    CUDA_11_2_CUDNN8 = "11.2-cudnn8"
    CUDA_11_3_CUDNN8 = "11.3-cudnn8"
    CUDA_11_4_CUDNN8 = "11.4-cudnn8"
    CUDA_11_5_CUDNN8 = "11.5-cudnn8"
    CUDA_11_6_CUDNN8 = "11.6-cudnn8"
    CUDA_11_7_CUDNN8 = "11.7-cudnn8"
    CUDA_11_8_CUDNN8 = "11.8-cudnn8"
    CUDA_12_0_CUDNN8 = "12.0-cudnn8"
    CUDA_12_1_CUDNN8 = "12.1-cudnn8"
    CUDA_12_2_CUDNN8 = "12.2-cudnn8"
    CUDA_12_3_CUDNN9 = "12.3-cudnn9"
    CUDA_12_4_CUDNN9 = "12.4-cudnn9"
    CUDA_12_5_CUDNN9 = "12.5-cudnn9"
    CUDA_12_6_CUDNN9 = "12.6-cudnn9"


class GPUType(str, enum.Enum):
    P4 = "P4"
    P100 = "P100"
    V100 = "V100"
    T4 = "T4"
    A10G = "A10G"
    A100_40GB = "A100_40GB"
    A100_80GB = "A100_80GB"
    L4 = "L4"
    H100_80GB = "H100_80GB"
    H100_94GB = "H100_94GB"
    H200 = "H200"


class TPUType(str, enum.Enum):
    V4_PODSLICE = "tpu-v4-podslice"
    V5_LITE_DEVICE = "tpu-v5-lite-device"
    V5_LITE_PODSLICE = "tpu-v5-lite-podslice"
    V5P_SLICE = "tpu-v5p-slice"


class AWSInferentiaAccelerator(str, enum.Enum):
    INF1 = "INF1"
    INF2 = "INF2"


class PatchedModelBase(BaseModel):
    class Config:
        extra = "forbid"


class DockerFileBuild(models.DockerFileBuild, PatchedModelBase):
    type: Literal["dockerfile"] = "dockerfile"

    @validator("build_args")
    def validate_build_args(cls, value):
        if not isinstance(value, dict):
            raise TypeError("build_args should be of type dict")
        for k, v in value.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise TypeError("build_args should have keys and values as string")
            if not k.strip() or not v.strip():
                raise ValueError("build_args cannot have empty keys or values")
        return value


class PythonBuild(models.PythonBuild, PatchedModelBase):
    type: Literal["tfy-python-buildpack"] = "tfy-python-buildpack"

    @root_validator
    def validate_values(cls, values):
        if values.get("cuda_version"):
            python_version = values.get("python_version")
            if python_version and not re.match(r"^3\.\d+$", python_version):
                raise ValueError(
                    f'`python_version` must be 3.x (e.g. "3.9") when `cuda_version` field is '
                    f"provided but got {python_version!r}. If you are adding a "
                    f'patch version, please remove it (e.g. "3.9.2" should be "3.9")'
                )
        _resolve_requirements_path(
            build_context_path=values.get("build_context_path") or "./",
            requirements_path=values.get("requirements_path"),
        )
        return values


class SparkBuild(models.SparkBuild, PatchedModelBase):
    type: Literal["tfy-spark-buildpack"] = "tfy-spark-buildpack"

    @root_validator
    def validate_values(cls, values):
        _resolve_requirements_path(
            build_context_path=values.get("build_context_path") or "./",
            requirements_path=values.get("requirements_path"),
        )
        return values


class SparkImageBuild(models.SparkImageBuild, PatchedModelBase):
    type: Literal["spark-image-build"] = "spark-image-build"


class SparkImage(models.SparkImage, PatchedModelBase):
    type: Literal["spark-image"] = "spark-image"


class RemoteSource(models.RemoteSource, PatchedModelBase):
    type: Literal["remote"] = "remote"


class LocalSource(models.LocalSource, PatchedModelBase):
    type: Literal["local"] = "local"


class Build(models.Build, PatchedModelBase):
    type: Literal["build"] = "build"
    build_source: Union[models.RemoteSource, models.GitSource, models.LocalSource] = (
        Field(default_factory=LocalSource)
    )


class Manual(models.Manual, PatchedModelBase):
    type: Literal["manual"] = "manual"


class Schedule(models.Schedule, PatchedModelBase):
    type: Literal["scheduled"] = "scheduled"


class GitSource(models.GitSource, PatchedModelBase):
    type: Literal["git"] = "git"


class HttpProbe(models.HttpProbe, PatchedModelBase):
    type: Literal["http"] = "http"


class BasicAuthCreds(models.BasicAuthCreds, PatchedModelBase):
    type: Literal["basic_auth"] = "basic_auth"


class JwtAuthConfig(models.JwtAuthConfig, PatchedModelBase):
    type: Literal["jwt_auth"] = "jwt_auth"


class TrueFoundryInteractiveLogin(models.TrueFoundryInteractiveLogin, PatchedModelBase):
    type: Literal["truefoundry_oauth"] = "truefoundry_oauth"


class HealthProbe(models.HealthProbe, PatchedModelBase):
    pass


class Image(models.Image, PatchedModelBase):
    type: Literal["image"] = "image"


class Port(models.Port, PatchedModelBase):
    app_protocol: Optional[models.AppProtocol] = Field(
        "http",
        description="+label=Application Protocol\n+usage=Application Protocol for the port.\nSelect the application protocol used by your service. For most use cases, this should be `http`(HTTP/1.1).\nIf you are running a gRPC server, select the `grpc` option.\nThis is only applicable if `expose=true`.",
    )

    @root_validator(pre=True)
    def app_protocol_set_default(cls, values):
        if values.get("app_protocol", None) is None:
            values["app_protocol"] = models.AppProtocol.http.value
        return values

    @root_validator(pre=True)
    def verify_host(cls, values):
        expose = values.get("expose", True)
        host = values.get("host", None)
        if expose:
            if not host:
                raise ValueError("Host must be provided to expose port")
            if not (
                re.fullmatch(
                    r"^((([a-zA-Z0-9\-]{1,63}\.)([a-zA-Z0-9\-]{1,63}\.)*([A-Za-z]{1,63}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))$",
                    host,
                )
            ):
                raise ValueError(
                    "Invalid value for `host`. A valid host must contain only alphanumeric letters and hypens e.g.  `ai.example.com`, `app.truefoundry.com`.\nYou can get the list of configured hosts for the cluster from the Integrations > Clusters page. Please see https://docs.truefoundry.com/docs/checking-configured-domain for more information."
                )
        else:
            if host:
                raise ValueError("Cannot pass host when expose=False")

        return values


class Resources(models.Resources, PatchedModelBase):
    pass


class Param(models.Param, PatchedModelBase):
    pass


class CPUUtilizationMetric(models.CPUUtilizationMetric, PatchedModelBase):
    type: Literal["cpu_utilization"] = "cpu_utilization"


class RPSMetric(models.RPSMetric, PatchedModelBase):
    type: Literal["rps"] = "rps"


class CronMetric(models.CronMetric, PatchedModelBase):
    type: Literal["cron"] = "cron"


class ServiceAutoscaling(models.ServiceAutoscaling, PatchedModelBase):
    pass


class AsyncServiceAutoscaling(models.AsyncServiceAutoscaling, PatchedModelBase):
    pass


class Autoscaling(ServiceAutoscaling):
    def __init__(self, **kwargs):
        warnings.warn(
            "`truefoundry.deploy.Autoscaling` is deprecated and will be removed in a future version. "
            "Please use `truefoundry.deploy.ServiceAutoscaling` instead. "
            "You can rename `Autoscaling` to `ServiceAutoscaling` in your script.",
            category=TrueFoundryDeprecationWarning,
            stacklevel=2,
        )
        super().__init__(**kwargs)


class BlueGreen(models.BlueGreen, PatchedModelBase):
    type: Literal["blue_green"] = "blue_green"


class Canary(models.Canary, PatchedModelBase):
    type: Literal["canary"] = "canary"


class Rolling(models.Rolling, PatchedModelBase):
    type: Literal["rolling_update"] = "rolling_update"


class SecretMount(models.SecretMount, PatchedModelBase):
    type: Literal["secret"] = "secret"


class StringDataMount(models.StringDataMount, PatchedModelBase):
    type: Literal["string"] = "string"


class VolumeMount(models.VolumeMount, PatchedModelBase):
    type: Literal["volume"] = "volume"


class NodeSelector(models.NodeSelector, PatchedModelBase):
    type: Literal["node_selector"] = "node_selector"


class NodepoolSelector(models.NodepoolSelector, PatchedModelBase):
    type: Literal["nodepool_selector"] = "nodepool_selector"


class Endpoint(models.Endpoint, PatchedModelBase):
    pass


class HelmRepo(models.HelmRepo, PatchedModelBase):
    type: Literal["helm-repo"] = "helm-repo"


class GitHelmRepo(models.GitHelmRepo, PatchedModelBase):
    type: Literal["git-helm-repo"] = "git-helm-repo"


class OCIRepo(models.OCIRepo, PatchedModelBase):
    type: Literal["oci-repo"] = "oci-repo"


class VolumeBrowser(models.VolumeBrowser, PatchedModelBase):
    pass


class WorkerConfig(models.WorkerConfig, PatchedModelBase):
    pass


class SQSInputConfig(models.SQSInputConfig, PatchedModelBase):
    type: Literal["sqs"] = "sqs"


class SQSOutputConfig(models.SQSOutputConfig, PatchedModelBase):
    type: Literal["sqs"] = "sqs"


class SQSQueueMetricConfig(models.SQSQueueMetricConfig, PatchedModelBase):
    type: Literal["sqs"] = "sqs"


class AWSAccessKeyAuth(models.AWSAccessKeyAuth, PatchedModelBase):
    pass


class NATSInputConfig(models.NATSInputConfig, PatchedModelBase):
    type: Literal["nats"] = "nats"


class CoreNATSOutputConfig(models.CoreNATSOutputConfig, PatchedModelBase):
    type: Literal["core-nats"] = "core-nats"


class NATSUserPasswordAuth(models.NATSUserPasswordAuth, PatchedModelBase):
    pass


class NATSOutputConfig(models.NATSOutputConfig, PatchedModelBase):
    type: Literal["nats"] = "nats"


class NATSMetricConfig(models.NATSMetricConfig, PatchedModelBase):
    type: Literal["nats"] = "nats"


class KafkaInputConfig(models.KafkaInputConfig, PatchedModelBase):
    type: Literal["kafka"] = "kafka"


class KafkaOutputConfig(models.KafkaOutputConfig, PatchedModelBase):
    type: Literal["kafka"] = "kafka"


class KafkaMetricConfig(models.KafkaMetricConfig, PatchedModelBase):
    type: Literal["kafka"] = "kafka"


class KafkaSASLAuth(models.KafkaSASLAuth, PatchedModelBase):
    pass


class AMQPInputConfig(models.AMQPInputConfig, PatchedModelBase):
    type: Literal["amqp"] = "amqp"


class AMQPOutputConfig(models.AMQPOutputConfig, PatchedModelBase):
    type: Literal["amqp"] = "amqp"


class AMQPMetricConfig(models.AMQPMetricConfig, PatchedModelBase):
    type: Literal["amqp"] = "amqp"


class AsyncProcessorSidecar(models.AsyncProcessorSidecar, PatchedModelBase):
    pass


class ArtifactsCacheVolume(models.ArtifactsCacheVolume, PatchedModelBase):
    pass


class HuggingfaceArtifactSource(models.HuggingfaceArtifactSource, PatchedModelBase):
    type: Literal["huggingface-hub"] = "huggingface-hub"


class TrueFoundryArtifactSource(models.TrueFoundryArtifactSource, PatchedModelBase):
    type: Literal["truefoundry-artifact"] = "truefoundry-artifact"


class ArtifactsDownload(models.ArtifactsDownload, PatchedModelBase):
    pass


class NvidiaGPU(models.NvidiaGPU, PatchedModelBase):
    type: Literal["nvidia_gpu"] = "nvidia_gpu"
    name: Optional[Union[GPUType, constr(regex=r"^tpu-[a-z\d\-]+$")]] = None  # type: ignore[valid-type]


class NvidiaMIGGPU(models.NvidiaMIGGPU, PatchedModelBase):
    type: Literal["nvidia_mig_gpu"] = "nvidia_mig_gpu"


class NvidiaTimeslicingGPU(models.NvidiaTimeslicingGPU, PatchedModelBase):
    type: Literal["nvidia_timeslicing_gpu"] = "nvidia_timeslicing_gpu"


class AWSInferentia(models.AWSInferentia, PatchedModelBase):
    type: Literal["aws_inferentia"] = "aws_inferentia"
    name: Optional[Union[AWSInferentiaAccelerator, str]] = None


class GcpTPU(models.GcpTPU, PatchedModelBase):
    type: Literal["gcp_tpu"] = "gcp_tpu"
    name: Union[TPUType, Literal[r"tpu-[a-z\d\-]+"]]


class DynamicVolumeConfig(models.DynamicVolumeConfig, PatchedModelBase):
    type: Literal["dynamic"] = "dynamic"


class StaticVolumeConfig(models.StaticVolumeConfig, PatchedModelBase):
    type: Literal["static"] = "static"


class PythonTaskConfig(models.PythonTaskConfig, PatchedModelBase):
    type: Literal["python-task-config"] = "python-task-config"
    resources: models.Resources = Field(default_factory=models.Resources)


class ContainerTaskConfig(models.ContainerTaskConfig, PatchedModelBase):
    type: Literal["container-task-config"] = "container-task-config"
    resources: models.Resources = Field(default_factory=models.Resources)


class TaskDockerFileBuild(models.TaskDockerFileBuild, PatchedModelBase):
    type: Literal["task-dockerfile-build"] = "task-dockerfile-build"


class TaskPythonBuild(models.TaskPythonBuild, PatchedModelBase):
    type: Literal["task-python-build"] = "task-python-build"


# Deprecated aliases, kept for backward compatibility
TruefoundryArtifactSource = TrueFoundryArtifactSource


class Email(models.Email, PatchedModelBase):
    type: Literal["email"] = "email"


class SlackWebhook(models.SlackWebhook, PatchedModelBase):
    type: Literal["slack-webhook"] = "slack-webhook"


class SlackBot(models.SlackBot, PatchedModelBase):
    type: Literal["slack-bot"] = "slack-bot"


class SparkJobScalaEntrypoint(models.SparkJobScalaEntrypoint, PatchedModelBase):
    type: Literal["scala"] = "scala"


class SparkJobPythonEntrypoint(models.SparkJobPythonEntrypoint, PatchedModelBase):
    type: Literal["python"] = "python"


class SparkJobJavaEntrypoint(models.SparkJobJavaEntrypoint, PatchedModelBase):
    type: Literal["java"] = "java"


class SparkJobPythonNotebookEntrypoint(
    models.SparkJobPythonNotebookEntrypoint, PatchedModelBase
):
    type: Literal["python-notebook"] = "python-notebook"


class SparkJobScalaNotebookEntrypoint(
    models.SparkJobScalaNotebookEntrypoint, PatchedModelBase
):
    type: Literal["scala-notebook"] = "scala-notebook"


class PySparkTaskConfig(models.PySparkTaskConfig, PatchedModelBase):
    type: Literal["pyspark-task-config"] = "pyspark-task-config"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            import truefoundry.workflow.spark_task as _  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "truefoundry.workflow.spark_task is not installed. Please install it with `pip install truefoundry[workflow,spark]`"
            ) from e


class SparkDriverConfig(models.SparkDriverConfig, PatchedModelBase):
    type: Literal["spark-driver-config"] = "spark-driver-config"


class SparkExecutorConfig(models.SparkExecutorConfig, PatchedModelBase):
    type: Literal["spark-executor-config"] = "spark-executor-config"


class SparkExecutorFixedInstances(models.SparkExecutorFixedInstances, PatchedModelBase):
    type: Literal["fixed"] = "fixed"


class SparkExecutorDynamicScaling(models.SparkExecutorDynamicScaling, PatchedModelBase):
    type: Literal["dynamic"] = "dynamic"


class TaskPySparkBuild(models.TaskPySparkBuild, PatchedModelBase):
    type: Literal["task-pyspark-build"] = "task-pyspark-build"
