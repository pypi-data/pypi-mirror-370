import re
from typing import Union


def get_application_fqn_from_deployment_fqn(deployment_fqn: str) -> str:
    if not re.search(r":\d+$", deployment_fqn):
        raise ValueError(
            "Invalid `deployment_fqn` format. A deployment fqn is supposed to end with a version number"
        )
    application_fqn, _ = deployment_fqn.rsplit(":", 1)
    return application_fqn


def get_deployment_fqn_from_application_fqn(
    application_fqn: str, version: Union[str, int]
) -> str:
    return f"{application_fqn}:{version}"


def find_list_paths(data, parent_key="", sep="."):
    list_paths = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            list_paths.extend(find_list_paths(value, new_key, sep))
    elif isinstance(data, list):
        list_paths.append(parent_key)
        for i, value in enumerate(data):
            new_key = f"{parent_key}[{i}]"
            list_paths.extend(find_list_paths(value, new_key, sep))
    return list_paths
