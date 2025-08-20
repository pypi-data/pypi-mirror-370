from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_REQUEST, INTERNAL_ERROR

UNAUTHORIZED = -32002
FORBIDDEN = -32003
THROTTLED = -32004


class BaseError(McpError):
    code: int

    def __init__(self, message: str, data: Any = None):
        error = ErrorData(
            code=self.code,
            message=message,
            data=data,
        )

        super().__init__(error)


class UnauthorizedError(BaseError):
    code = UNAUTHORIZED


class ForbiddenError(BaseError):
    code = FORBIDDEN


class InvalidRequestError(BaseError):
    code = INVALID_REQUEST


class ThrottledError(BaseError):
    code = THROTTLED


class InternalError(BaseError):
    code = INTERNAL_ERROR
