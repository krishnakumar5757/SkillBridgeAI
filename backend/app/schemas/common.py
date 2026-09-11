"""
SkillBridge AI — Common Pydantic Schemas

Shared schemas used across the application: health responses, error
responses, and pagination. Module-specific schemas will be added in
their respective module directories.
"""

from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Health Response
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    """Response schema for the health check endpoint."""

    status: str = Field(..., description="Overall health status: 'healthy' or 'unhealthy'")
    app: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    database: str = Field(
        ...,
        description="Database connectivity status: 'connected' or 'disconnected'",
    )


# ---------------------------------------------------------------------------
# Error Response (Architecture Section 9.8)
# ---------------------------------------------------------------------------
class ErrorDetail(BaseModel):
    """Error detail schema matching the architecture's error format."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional error context",
    )


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""

    error: ErrorDetail


# ---------------------------------------------------------------------------
# Pagination (for future list endpoints)
# ---------------------------------------------------------------------------
class PaginationParams(BaseModel):
    """Pagination query parameters for list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    items: list[Any] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    limit: int = Field(default=20)
    pages: int = Field(default=0)
