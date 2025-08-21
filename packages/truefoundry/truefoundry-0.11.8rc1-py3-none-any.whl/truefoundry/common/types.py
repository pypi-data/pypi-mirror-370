from typing import Protocol


class UploadCodePackageCallable(Protocol):
    def __call__(
        self, workspace_fqn: str, component_name: str, package_local_path: str
    ) -> str: ...
