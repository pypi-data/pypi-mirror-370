from flytekit import ContainerTask

from truefoundry.workflow import ContainerTaskConfig


class ContainerTask(ContainerTask):
    def __init__(self, name: str, task_config: ContainerTaskConfig):
        super().__init__(name=name, image="", command=[])
        self.tfy_task_config = task_config

    def get_custom(self, settings) -> dict:
        return {"truefoundry": self.tfy_task_config.dict()}
