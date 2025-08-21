from __future__ import annotations

import os
from typing import Any, Generator, List, Optional

from truefoundry.autodeploy.constants import MAX_FILE_SIZE_READ
from truefoundry.autodeploy.tools.base import (
    Event,
    Message,
    RequestEvent,
    ResponseEvent,
    Rule,
    Tool,
)
from truefoundry.pydantic_v1 import BaseModel, Field


class Line(BaseModel):
    line_number: int
    content: str


class ReadFile(Tool):
    description = """
Read contents of a file.
Avoid reading *.lock type files as they tend to be large
"""

    class Request(RequestEvent):
        path: str = Field(
            ...,
            pattern=r"^[a-zA-Z0-9\.]{1}.*$",
            description="File path to open. ",
        )

    class Response(ResponseEvent):
        data: Optional[List[Line]] = Field(
            None,
            description="Content of the file.",
        )
        error: Optional[str] = Field(
            None,
            description="Error while opening a file.",
        )

    def __init__(
        self,
        project_root_path: str,
    ):
        self.project_root_path = project_root_path

    def run(self, request: ReadFile.Request) -> Generator[Event, Any, ResponseEvent]:
        yield Rule(message="[bold green] Read files[/]")
        yield Message(
            message=f"[bold cyan]Processing:[/] Reading file at [magenta]{request.path}[/] and extracting details..."
        )

        try:
            file_path = os.path.join(self.project_root_path, request.path)
            file_size = os.path.getsize(file_path)

            if file_size > MAX_FILE_SIZE_READ:
                return ReadFile.Response(
                    error=f"File size exceeds {MAX_FILE_SIZE_READ} bytes limit"
                )

            with open(file_path, "r", encoding="utf8") as f:
                response = ReadFile.Response(data=[])
                for i, line in enumerate(f):
                    response.data.append(Line(line_number=i + 1, content=line))
                return response
        except FileNotFoundError as ex:
            return ReadFile.Response(error=str(ex))
        except UnicodeDecodeError:
            return ReadFile.Response(
                error="This is a binary file, reading it is prohibited."
            )
