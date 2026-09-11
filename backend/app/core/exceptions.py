"""
SkillBridge AI — Custom Exceptions and Error Handlers

Defines application-level exceptions and FastAPI exception handlers
that produce consistent error responses per the architecture's
error format (Section 9.8).
"""

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# ---------------------------------------------------------------------------
# Custom Application Exceptions
# ---------------------------------------------------------------------------
class SkillBridgeError(Exception):
    """Base exception for all SkillBridge application errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(SkillBridgeError):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str, resource_id: str | None = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} '{resource_id}' not found"
        super().__init__(code="NOT_FOUND", message=message, status_code=404)


class ValidationError(SkillBridgeError):
    """Raised when input validation fails at the application level."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            details=details,
        )


class AuthenticationError(SkillBridgeError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(code="AUTHENTICATION_ERROR", message=message, status_code=401)


class AuthorizationError(SkillBridgeError):
    """Raised when a user is not authorized to access a resource."""

    def __init__(self, message: str = "Not authorized to access this resource"):
        super().__init__(code="AUTHORIZATION_ERROR", message=message, status_code=403)


# ---------------------------------------------------------------------------
# Error Response Builder
# ---------------------------------------------------------------------------
def _error_response(
    code: str,
    message: str,
    status_code: int,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Build a JSON error response in the architecture's format.

    Format (Section 9.8):
        {
            "error": {
                "code": "...",
                "message": "...",
                "details": {}
            }
        }
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


# ---------------------------------------------------------------------------
# Exception Handlers Registration
# ---------------------------------------------------------------------------
def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""

    @app.exception_handler(SkillBridgeError)
    async def skillbridge_error_handler(request: Request, exc: SkillBridgeError):
        return _error_response(exc.code, exc.message, exc.status_code, exc.details)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return _error_response("HTTP_ERROR", str(exc.detail), exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ):
        return _error_response(
            "VALIDATION_ERROR",
            "Request validation failed",
            422,
            details={"errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Log the full exception but return a generic message to the client.
        # Do not leak internal details in production.
        from app.core.logging import get_logger

        logger = get_logger("app.exceptions")
        logger.exception("Unhandled exception: %s", exc)
        return _error_response(
            "INTERNAL_ERROR",
            "An internal server error occurred",
            500,
        )
