import warnings
from typing import Any, Literal, Union

from truefoundry.common.warnings import TrueFoundryDeprecationWarning
from truefoundry.deploy._autogen import models
from truefoundry.deploy.lib.model.entity import Deployment
from truefoundry.deploy.v2.lib.deploy import deploy_component
from truefoundry.deploy.v2.lib.patched_models import LocalSource
from truefoundry.pydantic_v1 import BaseModel, Field, conint, root_validator, validator

_TRIGGER_ON_DEPLOY_DEPRECATION_MESSAGE = """
Setting `trigger_on_deploy` in manifest has been deprecated and the field will be removed in future releases.

Please remove it from the spec and instead use

`trigger_on_deploy` argument on `.deploy`

E.g.

```
job = Job(...)  # remove `trigger_on_deploy` from initialization
job.deploy(..., trigger_on_deploy={arg_value})
```

OR

`{flag}` option on `tfy deploy`

E.g.

```
tfy deploy -f truefoundry.yaml {flag}
```
"""


def _warn_if_trigger_on_deploy_used(_klass, v: Any) -> Any:
    if v is not None:
        # v is the value of trigger_on_deploy, which is also the arg_value for the message
        flag = "--trigger-on-deploy" if v else "--no-trigger-on-deploy"
        warnings.warn(
            _TRIGGER_ON_DEPLOY_DEPRECATION_MESSAGE.format(arg_value=v, flag=flag),
            TrueFoundryDeprecationWarning,
            stacklevel=2,
        )
    return v


class DeployablePatchedModelBase(BaseModel):
    class Config:
        extra = "forbid"

    def deploy(
        self,
        workspace_fqn: str,
        wait: bool = True,
        force: bool = False,
        trigger_on_deploy: bool = False,
    ) -> Deployment:
        return deploy_component(
            component=self,
            workspace_fqn=workspace_fqn,
            wait=wait,
            force=force,
            trigger_on_deploy=trigger_on_deploy,
        )


class Service(models.Service, DeployablePatchedModelBase):
    type: Literal["service"] = "service"
    resources: models.Resources = Field(default_factory=models.Resources)
    # This is being patched because cue export marks this as a "number"
    replicas: Union[conint(ge=0, le=100), models.ServiceAutoscaling] = Field(  # type: ignore[valid-type]
        1,
        description="+label=Replicas\n+usage=Replicas of service you want to run\n+icon=fa-clone\n+sort=3",
    )


class Job(models.Job, DeployablePatchedModelBase):
    type: Literal["job"] = "job"
    resources: models.Resources = Field(default_factory=models.Resources)

    @validator("trigger_on_deploy")
    def _warn_if_trigger_on_deploy_used(cls, v: Any) -> Any:
        return _warn_if_trigger_on_deploy_used(cls, v)


class SparkJob(models.SparkJob, DeployablePatchedModelBase):
    type: Literal["spark-job"] = "spark-job"


class Notebook(models.Notebook, DeployablePatchedModelBase):
    type: Literal["notebook"] = "notebook"
    resources: models.Resources = Field(default_factory=models.Resources)


class Codeserver(models.Codeserver, DeployablePatchedModelBase):
    type: Literal["codeserver"] = "codeserver"
    resources: models.Resources = Field(default_factory=models.Resources)


class RStudio(models.RStudio, DeployablePatchedModelBase):
    type: Literal["rstudio"] = "rstudio"
    resources: models.Resources = Field(default_factory=models.Resources)


class Helm(models.Helm, DeployablePatchedModelBase):
    type: Literal["helm"] = "helm"


class Volume(models.Volume, DeployablePatchedModelBase):
    type: Literal["volume"] = "volume"


class ApplicationSet(models.ApplicationSet, DeployablePatchedModelBase):
    type: Literal["application-set"] = "application-set"


class AsyncService(models.AsyncService, DeployablePatchedModelBase):
    type: Literal["async-service"] = "async-service"
    replicas: Union[conint(ge=0, le=100), models.AsyncServiceAutoscaling] = 1  # type: ignore[valid-type]
    resources: models.Resources = Field(default_factory=models.Resources)


class SSHServer(models.SSHServer, DeployablePatchedModelBase):
    type: Literal["ssh-server"] = "ssh-server"
    resources: models.Resources = Field(default_factory=models.Resources)


class Workflow(models.Workflow, DeployablePatchedModelBase):
    type: Literal["workflow"] = "workflow"
    source: Union[models.RemoteSource, models.LocalSource] = Field(
        default_factory=lambda: LocalSource(local_build=False)
    )

    def deploy(
        self, workspace_fqn: str, wait: bool = True, force: bool = False
    ) -> Deployment:
        from truefoundry.deploy.v2.lib.deploy_workflow import deploy_workflow

        return deploy_workflow(
            workflow=self, workspace_fqn=workspace_fqn, wait=wait, force=force
        )


class Application(models.Application, DeployablePatchedModelBase):
    # We need a discriminator field to the root model to simplify the Validation errors
    # Unfortunately cue export cannot add discriminator in OAS
    # Even if we add it manually in OAS, `datamodel-code-generator` has bugs when discriminator field is enum type in member models.
    # It will change the members to be incorrect like this
    # >>> class Service(BaseModel):
    # >>>     type: Literal["Service"] = Field("Service")  # notice the capital casing
    # This is why we add it manually here
    __root__: Union[
        models.Service,
        models.AsyncService,
        models.Job,
        models.Notebook,
        models.Codeserver,
        models.SSHServer,
        models.RStudio,
        models.Helm,
        models.Volume,
        models.ApplicationSet,
        models.Workflow,
        models.SparkJob,
    ] = Field(..., description="", discriminator="type")

    @root_validator(pre=True)
    def _validate_spec(cls, values: Any) -> Any:
        if isinstance(values, dict) and "__root__" in values:
            root = values["__root__"]
            if (
                isinstance(root, dict)
                and root.get("type") == "job"
                and root.get("trigger_on_deploy") is not None
            ):
                _warn_if_trigger_on_deploy_used(cls, root.get("trigger_on_deploy"))
        return values

    def deploy(
        self,
        workspace_fqn: str,
        wait: bool = True,
        force: bool = False,
        trigger_on_deploy: bool = False,
    ) -> Deployment:
        if isinstance(self.__root__, models.Workflow):
            from truefoundry.deploy.v2.lib.deploy_workflow import deploy_workflow

            return deploy_workflow(
                workflow=self.__root__,
                workspace_fqn=workspace_fqn,
                wait=wait,
                force=force,
            )
        else:
            return deploy_component(
                component=self.__root__,
                workspace_fqn=workspace_fqn,
                wait=wait,
                force=force,
                trigger_on_deploy=trigger_on_deploy,
            )
