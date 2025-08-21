import ast
import io
import json
import re
from typing import Any, Callable, Dict, List, Optional

from rich.console import Console
from rich.pretty import pprint

from truefoundry.deploy import Application, LocalSource
from truefoundry.pydantic_v1 import BaseModel


def generate_deployment_code(
    symbols_to_import: List[str],
    application_type: str,
    spec_repr: str,
    workspace_fqn: str,
):
    symbols = ", ".join(symbols_to_import)
    application_type = application_type.replace(" ", "").replace("-", "_")
    code = f"""\
import logging
from truefoundry.deploy import (
    {symbols},
)
logging.basicConfig(level=logging.INFO)

{application_type} = {spec_repr}

{application_type}.deploy(workspace_fqn="{workspace_fqn}", wait=False)\
"""
    return code


def extract_class_names(code):
    tree = ast.parse(code)

    # Function to extract keywords from the AST
    def extract_class_names_from_ast_tree(node):
        keywords = set()
        for child_node in ast.iter_child_nodes(node):
            if isinstance(child_node, ast.Call):
                keywords.add(child_node.func.id)
            keywords.update(extract_class_names_from_ast_tree(child_node))
        return keywords

    # Get keywords from the main body of the code
    main_keywords = extract_class_names_from_ast_tree(tree)
    return list(main_keywords)


def replace_enums_with_values(raw_str):
    # required to replace enums of format <AppProtocol.HTTP: 'http'> with 'http'
    pattern = r'<([a-zA-Z0-9_]+).[a-zA-Z0-9_]+: [\'"](.+)[\'"]>'
    replacement = r"'\2'"

    result = re.sub(pattern, replacement, raw_str)
    return result


def remove_none_type_fields(code):
    lines = code.split("\n")
    new_lines = [
        line
        for line in lines
        if not (line.endswith("=None") or line.endswith("=None,"))
    ]
    formatted_code = "\n".join(new_lines)
    return formatted_code


def remove_type_field(code):
    lines = code.split("\n")
    new_lines = [re.sub(r'^[ \t]*type=[\'"][^"]*[\'"],?', "", line) for line in lines]
    return "\n".join(new_lines)


def add_deploy_line(code, workspace_fqn, application_type):
    deploy_line = f"{application_type}.deploy('workspace_fqn={workspace_fqn}')"
    return code + "\n" + deploy_line


def get_python_repr(obj):
    stream = io.StringIO()
    console = Console(file=stream, no_color=True, highlighter=None)
    pprint(obj, expand_all=True, console=console, indent_guides=False)
    return stream.getvalue()


COMMENT_FOR_LOCAL_SOURCE = """# Set build_source=LocalSource(local_build=False), in order to deploy code from your local.
# With local_build=False flag, docker image will be built on cloud instead of local
# Else it will try to use docker installed on your local machine to build the image"""


def add_local_source_comment(code):
    lines = code.split("\n")
    new_lines = []
    for line in lines:
        if line.lstrip(" ").startswith("build_source=GitSource"):
            new_lines.append(COMMENT_FOR_LOCAL_SOURCE)
        new_lines.append(line)
    return "\n".join(new_lines)


def _convert_deployment_config_to_python(workspace_fqn: str, application_spec: dict):
    """
    Convert a deployment config to a python file that can be used to deploy to a workspace
    """
    application = Application.parse_obj(application_spec)
    application_obj = application.__root__
    application_type = application_obj.type
    if (
        hasattr(application_obj, "image")
        and hasattr(application_obj.image, "type")
        and application_obj.image.type == "build"
        and application_obj.image.build_source.type == "remote"
    ):
        application_obj.image.build_source = LocalSource(local_build=False)

    spec_repr = get_python_repr(application_obj)
    spec_repr = replace_enums_with_values(spec_repr)
    spec_repr = remove_none_type_fields(spec_repr)
    spec_repr = remove_type_field(spec_repr)

    # extract class names to import
    symbols_to_import = extract_class_names(spec_repr)

    # check if GitSource exists in array of symbols to import
    if "GitSource" in symbols_to_import:
        symbols_to_import.append("LocalSource")

    generated_code = generate_deployment_code(
        symbols_to_import=symbols_to_import,
        application_type=application_type,
        spec_repr=spec_repr,
        workspace_fqn=workspace_fqn,
    )

    if "GitSource" in symbols_to_import:
        generated_code = add_local_source_comment(generated_code)

    return generated_code


def _default_exclude_fn(model: BaseModel, name: str) -> bool:
    return False


def convert_deployment_config_to_python(
    workspace_fqn: str,
    application_spec: Dict[str, Any],
    exclude_fn: Callable[[BaseModel, str], bool] = _default_exclude_fn,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
):
    original_repr_args = BaseModel.__repr_args__

    def _patched_repr_args(self: BaseModel):
        _missing = object()
        pairs = []
        for name, value in original_repr_args(self):
            if name is not None:
                if exclude_fn(self, name):
                    continue
                if exclude_unset and name not in self.__fields_set__:
                    continue
                model_field = self.__fields__.get(name)
                if model_field is None:
                    continue
                if (
                    exclude_defaults
                    and not getattr(model_field, "required", True)
                    and getattr(model_field, "default", _missing) == value
                ):
                    continue
            pairs.append((name, value))
        return pairs

    try:
        BaseModel.__repr_args__ = _patched_repr_args
        return _convert_deployment_config_to_python(
            workspace_fqn=workspace_fqn, application_spec=application_spec
        )
    finally:
        BaseModel.__repr_args__ = original_repr_args


def generate_python_snippet_for_trigger_job(
    application_fqn: str,
    command: Optional[str],
    params: Optional[Dict[str, str]],
    run_name_alias: Optional[str],
):
    job_run_python_template = """\
from truefoundry.deploy import trigger_job

response = trigger_job(
  application_fqn="{{application_fqn}}",
  # You can pass command or params, but not both
  # command={{command}},
  # params={{params}},
  # run_name_alias={{run_name_alias}}
)

print(response.jobRunName)
"""
    output_python_str = job_run_python_template.replace(
        "{{application_fqn}}", application_fqn
    )

    if command is not None:
        output_python_str = output_python_str.replace("# command", "command")
        output_python_str = output_python_str.replace("{{command}}", repr(command))
    else:
        output_python_str = output_python_str.replace(
            "{{command}}", "<Enter Command Here>"
        )

    if params is not None:
        output_python_str = output_python_str.replace("# params", "params")
        output_python_str = output_python_str.replace("{{params}}", repr(params))
    else:
        output_python_str = output_python_str.replace(
            "{{params}}", "<Enter Params(key-value pairs) here as python dict>"
        )
    if run_name_alias is not None:
        output_python_str = output_python_str.replace(
            "# run_name_alias", "run_name_alias"
        )
        output_python_str = output_python_str.replace(
            "{{run_name_alias}}", repr(run_name_alias)
        )
    else:
        output_python_str = output_python_str.replace(
            "{{run_name_alias}}", "<Enter Run Name Alias here>"
        )

    return output_python_str


def generate_curl_snippet_for_trigger_job(
    control_plane_url: str,
    application_id: str,
    command: Optional[str],
    params: Optional[Dict[str, str]],
    run_name_alias: Optional[str],
):
    job_run_curl_request_template = """curl -X 'POST' \\
  '{{control_plane_url}}/api/svc/v1/jobs/trigger' \\
  -H 'accept: */*' \\
  -H 'Authorization: Bearer <Paste your API key here. You can generate it from the Settings Page>' \\
  -H 'Content-Type: application/json' \\
  -d '{
  "applicationId": "{{application_id}}",
  "input": {{input}},
  "metadata": {
    "job_run_name_alias": "{{run_name_alias}}"
  }
}'
"""
    output_curl_str = job_run_curl_request_template.replace(
        "{{control_plane_url}}", control_plane_url.rstrip("/")
    )
    output_curl_str = output_curl_str.replace("{{application_id}}", application_id)
    output_curl_str = output_curl_str.replace(
        "{{input}}", json.dumps({"command": command, "params": params}, indent=2)
    )
    if run_name_alias is not None:
        output_curl_str = output_curl_str.replace("{{run_name_alias}}", run_name_alias)
    else:
        output_curl_str = output_curl_str.replace(
            "{{run_name_alias}}", "<Enter Run Name Alias here>"
        )
    return output_curl_str
