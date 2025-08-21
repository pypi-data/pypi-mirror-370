from typing import Optional


# TODO (chiragjn): We need to establish uniform exception handling across codebase
class HttpRequestException(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = str(message)
        self.status_code = status_code
        super().__init__(message)

    def __str__(self) -> str:
        return self.message or ""


class BadRequestException(HttpRequestException):
    pass
