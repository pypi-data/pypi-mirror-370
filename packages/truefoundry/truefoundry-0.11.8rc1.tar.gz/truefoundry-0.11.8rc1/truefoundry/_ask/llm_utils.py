import copy
import datetime
import json
import re
import warnings
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, List, Literal, Optional, cast

from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolParam,
)
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

# Taken from https://github.com/pydantic/pydantic-ai/blob/222bec41e28fb96b49e71609c43b683d97d1dc97/pydantic_ai_slim/pydantic_ai/models/gemini.py#L791

JsonSchema = dict[str, Any]


@dataclass(init=False)
class WalkJsonSchema(ABC):
    """Walks a JSON schema, applying transformations to it at each level.

    Note: We may eventually want to rework tools to build the JSON schema from the type directly, using a subclass of
    pydantic.json_schema.GenerateJsonSchema, rather than making use of this machinery.
    """

    def __init__(
        self,
        schema: JsonSchema,
        *,
        prefer_inlined_defs: bool = False,
        simplify_nullable_unions: bool = False,
    ):
        self.schema = schema
        self.prefer_inlined_defs = prefer_inlined_defs
        self.simplify_nullable_unions = simplify_nullable_unions

        self.defs: dict[str, JsonSchema] = self.schema.get("$defs", {})
        self.refs_stack: list[str] = []
        self.recursive_refs = set[str]()

    @abstractmethod
    def transform(self, schema: JsonSchema) -> JsonSchema:
        """Make changes to the schema."""
        return schema

    def walk(self) -> JsonSchema:
        schema = copy.deepcopy(self.schema)

        # First, handle everything but $defs:
        schema.pop("$defs", None)
        handled = self._handle(schema)

        if not self.prefer_inlined_defs and self.defs:
            handled["$defs"] = {k: self._handle(v) for k, v in self.defs.items()}

        elif self.recursive_refs:  # pragma: no cover
            # If we are preferring inlined defs and there are recursive refs, we _have_ to use a $defs+$ref structure
            # We try to use whatever the original root key was, but if it is already in use,
            # we modify it to avoid collisions.
            defs = {key: self.defs[key] for key in self.recursive_refs}
            root_ref = self.schema.get("$ref")
            root_key = None if root_ref is None else re.sub(r"^#/\$defs/", "", root_ref)
            if root_key is None:
                root_key = self.schema.get("title", "root")
                while root_key in defs:
                    # Modify the root key until it is not already in use
                    root_key = f"{root_key}_root"

            defs[root_key] = handled
            return {"$defs": defs, "$ref": f"#/$defs/{root_key}"}

        return handled

    def _handle(self, schema: JsonSchema) -> JsonSchema:
        nested_refs = 0
        if self.prefer_inlined_defs:
            while ref := schema.get("$ref"):
                key = re.sub(r"^#/\$defs/", "", ref)
                if key in self.refs_stack:
                    self.recursive_refs.add(key)
                    break  # recursive ref can't be unpacked
                self.refs_stack.append(key)
                nested_refs += 1

                def_schema = self.defs.get(key)
                if def_schema is None:  # pragma: no cover
                    raise ValueError(f"Could not find $ref definition for {key}")
                schema = def_schema

        # Handle the schema based on its type / structure
        type_ = schema.get("type")
        if type_ == "object":
            schema = self._handle_object(schema)
        elif type_ == "array":
            schema = self._handle_array(schema)
        elif type_ is None:
            schema = self._handle_union(schema, "anyOf")
            schema = self._handle_union(schema, "oneOf")

        # Apply the base transform
        schema = self.transform(schema)

        if nested_refs > 0:
            self.refs_stack = self.refs_stack[:-nested_refs]

        return schema

    def _handle_object(self, schema: JsonSchema) -> JsonSchema:
        if properties := schema.get("properties"):
            handled_properties = {}
            for key, value in properties.items():
                handled_properties[key] = self._handle(value)
            schema["properties"] = handled_properties

        if (additional_properties := schema.get("additionalProperties")) is not None:
            if isinstance(additional_properties, bool):
                schema["additionalProperties"] = additional_properties
            else:
                schema["additionalProperties"] = self._handle(additional_properties)

        if (pattern_properties := schema.get("patternProperties")) is not None:
            handled_pattern_properties = {}
            for key, value in pattern_properties.items():
                handled_pattern_properties[key] = self._handle(value)
            schema["patternProperties"] = handled_pattern_properties

        return schema

    def _handle_array(self, schema: JsonSchema) -> JsonSchema:
        if prefix_items := schema.get("prefixItems"):
            schema["prefixItems"] = [self._handle(item) for item in prefix_items]

        if items := schema.get("items"):
            schema["items"] = self._handle(items)

        return schema

    def _handle_union(
        self, schema: JsonSchema, union_kind: Literal["anyOf", "oneOf"]
    ) -> JsonSchema:
        members = schema.get(union_kind)
        if not members:
            return schema

        handled = [self._handle(member) for member in members]

        # convert nullable unions to nullable types
        if self.simplify_nullable_unions:
            handled = self._simplify_nullable_union(handled)

        if len(handled) == 1:
            # In this case, no need to retain the union
            return handled[0]

        # If we have keys besides the union kind (such as title or discriminator), keep them without modifications
        schema = schema.copy()
        schema[union_kind] = handled
        return schema

    @staticmethod
    def _simplify_nullable_union(cases: list[JsonSchema]) -> list[JsonSchema]:
        # TODO: Should we move this to relevant subclasses? Or is it worth keeping here to make reuse easier?
        if len(cases) == 2 and {"type": "null"} in cases:
            # Find the non-null schema
            non_null_schema = next(
                (item for item in cases if item != {"type": "null"}),
                None,
            )
            if non_null_schema:
                # Create a new schema based on the non-null part, mark as nullable
                new_schema = copy.deepcopy(non_null_schema)
                new_schema["nullable"] = True
                return [new_schema]
            else:  # pragma: no cover
                # they are both null, so just return one of them
                return [cases[0]]

        return cases  # pragma: no cover


class _GeminiJsonSchema(WalkJsonSchema):
    """Transforms the JSON Schema from Pydantic to be suitable for Gemini.

    Gemini which [supports](https://ai.google.dev/gemini-api/docs/function-calling#function_declarations)
    a subset of OpenAPI v3.0.3.

    Specifically:
    * gemini doesn't allow the `title` keyword to be set
    * gemini doesn't allow `$defs` — we need to inline the definitions where possible
    """

    def __init__(self, schema: JsonSchema):
        super().__init__(
            schema, prefer_inlined_defs=True, simplify_nullable_unions=True
        )

    def transform(self, schema: JsonSchema) -> JsonSchema:  # noqa: C901
        # Note: we need to remove `additionalProperties: False` since it is currently mishandled by Gemini
        additional_properties = schema.pop(
            "additionalProperties", None
        )  # don't pop yet so it's included in the warning
        if additional_properties:
            original_schema = {**schema, "additionalProperties": additional_properties}
            warnings.warn(
                "`additionalProperties` is not supported by Gemini; it will be removed from the tool JSON schema."
                f" Full schema: {self.schema}\n\n"
                f"Source of additionalProperties within the full schema: {original_schema}\n\n"
                "If this came from a field with a type like `dict[str, MyType]`, that field will always be empty.\n\n"
                "If Google's APIs are updated to support this properly, please create an issue on the PydanticAI GitHub"
                " and we will fix this behavior.",
                UserWarning,
                stacklevel=2,
            )

        schema.pop("title", None)
        schema.pop("default", None)
        schema.pop("$schema", None)
        if (const := schema.pop("const", None)) is not None:  # pragma: no cover
            # Gemini doesn't support const, but it does support enum with a single value
            schema["enum"] = [const]
        schema.pop("discriminator", None)
        schema.pop("examples", None)

        # TODO: Should we use the trick from pydantic_ai.models.openai._OpenAIJsonSchema
        #   where we add notes about these properties to the field description?
        schema.pop("exclusiveMaximum", None)
        schema.pop("exclusiveMinimum", None)

        # Gemini only supports string enums, so we need to convert any enum values to strings.
        # Pydantic will take care of transforming the transformed string values to the correct type.
        if enum := schema.get("enum"):
            schema["type"] = "string"
            schema["enum"] = [str(val) for val in enum]

        type_ = schema.get("type")
        if "oneOf" in schema and "type" not in schema:  # pragma: no cover
            # This gets hit when we have a discriminated union
            # Gemini returns an API error in this case even though it says in its error message it shouldn't...
            # Changing the oneOf to an anyOf prevents the API error and I think is functionally equivalent
            schema["anyOf"] = schema.pop("oneOf")

        if type_ == "string" and (fmt := schema.pop("format", None)):
            description = schema.get("description")
            if description:
                schema["description"] = f"{description} (format: {fmt})"
            else:
                schema["description"] = f"Format: {fmt}"

        if "$ref" in schema:
            raise ValueError(
                f"Recursive `$ref`s in JSON Schema are not supported by Gemini: {schema['$ref']}"
            )

        if "prefixItems" in schema:
            # prefixItems is not currently supported in Gemini, so we convert it to items for best compatibility
            prefix_items = schema.pop("prefixItems")
            items = schema.get("items")
            unique_items = [items] if items is not None else []
            for item in prefix_items:
                if item not in unique_items:
                    unique_items.append(item)
            if len(unique_items) > 1:  # pragma: no cover
                schema["items"] = {"anyOf": unique_items}
            elif len(unique_items) == 1:
                schema["items"] = unique_items[0]
            schema.setdefault("minItems", len(prefix_items))
            if items is None:
                schema.setdefault("maxItems", len(prefix_items))

        return schema


def translate_tools_for_gemini(
    tools: Optional[List[ChatCompletionToolParam]],
) -> Optional[List[ChatCompletionToolParam]]:
    if tools is None:
        return None
    tools = copy.deepcopy(tools)
    for tool in tools:
        if "parameters" in tool["function"]:
            tool["function"]["parameters"] = _GeminiJsonSchema(
                tool["function"]["parameters"]
            ).walk()

    return tools


def log_chat_completion_message(
    message: ChatCompletionMessageParam, console: Console
) -> None:
    timestamp = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
    code_theme = "github-dark"
    try:
        _content = message.get("content") or ""
        message_content = f"```json\n{json.dumps(json.loads(_content), indent=2)}\n```"
    except (TypeError, ValueError):
        message_content = str(message.get("content") or "")

    tool_calls: Iterable[ChatCompletionMessageToolCallParam] = cast(
        list[ChatCompletionMessageToolCallParam],
        message.get("tool_calls", []),
    )

    rendered_content: list[Markdown | Text] = []

    if bool(message_content.strip()):
        rendered_content.append(Markdown(markup=message_content, code_theme=code_theme))

    for call in tool_calls:
        assert isinstance(call, ChatCompletionMessageToolCall)
        name = call.function.name
        args = call.function.arguments
        rendered_content.append(
            Text.from_markup(
                "[bold magenta]Tool Calls:[/bold magenta]\n",
                overflow="fold",
            )
        )
        rendered_content.append(
            Markdown(markup=f"```python\n▶ {name}({args})\n```", code_theme=code_theme)
        )

    if not rendered_content:
        return

    panel = Panel(
        Group(*rendered_content, fit=True),
        title=f"[bold blue]{timestamp}[/bold blue]",
        title_align="left",
        border_style="bright_blue",
        padding=(1, 2),
        expand=True,
        width=console.width,
    )
    console.print(panel)
