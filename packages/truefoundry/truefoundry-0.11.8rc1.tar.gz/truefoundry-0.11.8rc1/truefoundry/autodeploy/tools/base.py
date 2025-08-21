from __future__ import annotations

from typing import Any, ClassVar, Generator, Optional, Protocol, Type

from rich.console import Console

from truefoundry.pydantic_v1 import BaseModel


class Event(BaseModel):
    def render(self, _: Console) -> Optional[Any]: ...


class RequestEvent(Event): ...


class ResponseEvent(Event): ...


class Tool(Protocol):
    description: ClassVar[str]
    Request: ClassVar[Type[RequestEvent]]
    Response: ClassVar[Type[ResponseEvent]]

    def run(self, request: RequestEvent) -> Generator[Event, Any, ResponseEvent]: ...


class Message(Event):
    message: Any

    def render(self, console: Console):
        console.print(self.message)


class Rule(Event):
    message: Any

    def render(self, console: Console):
        console.rule(self.message)
