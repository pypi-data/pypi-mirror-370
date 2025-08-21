import re
from typing import Any, Dict, Optional

from truefoundry_sdk import ChatPromptManifest

_VAR_PATTERN = re.compile(r"\{\{(\w+)\}\}")


def render_text(template: str, variables: Dict[str, str]) -> str:
    return _VAR_PATTERN.sub(
        lambda m: (variables.get(m.group(1), f"{{{{{m.group(1)}}}}}")), template
    )


def render_prompt(
    prompt_template: ChatPromptManifest, variables: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Renders a prompt template with the provided variables.
    Args:
        prompt_template (ChatPromptManifest): The prompt template to render.
        variables (Optional[Dict[str, str]]): A dictionary of variables to replace in the template.
            If None, the default variables from the prompt template will be used.

    Returns:
        Dict[str, Any]: A dictionary containing the rendered messages and model configuration.

    """
    # Render the messages in the prompt template with the provided variables and default variables
    rendered_messages = []
    variables = {**(prompt_template.variables or {}), **(variables or {})}
    messages = [message.copy(deep=True) for message in prompt_template.messages]

    # Render the messages with the provided variables, if any
    if variables:
        for msg in messages:
            if isinstance(msg.content, str):
                msg.content = render_text(template=msg.content, variables=variables)
            elif isinstance(msg.content, list):
                for part in msg.content:
                    if part.type == "image_url" and isinstance(part.image_url.url, str):
                        part.image_url.url = render_text(
                            part.image_url.url, variables=variables
                        )
                    elif part.type == "text" and isinstance(part.text, str):
                        part.text = render_text(part.text, variables=variables)

    rendered_messages = [message.dict() for message in messages]

    # Merge parameters from model_configuration and extra_parameters
    model_configuration = prompt_template.model_configuration
    if model_configuration:
        model = model_configuration.model
        parameters = {
            **(
                model_configuration.parameters.dict()
                if model_configuration.parameters
                else {}
            ),
            **(model_configuration.extra_parameters or {}),
        }
    else:
        model = None
        parameters = {}

    return {
        "messages": rendered_messages,
        "model": model,
        "parameters": {k: v for k, v in parameters.items() if v is not None},
    }
