"""
SkillBridge AI — Health Check Endpoint

Provides a simple health check endpoint that verifies the backend
is running and the database is reachable.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])
logger = get_logger("app.routes.health")


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """Check the health of the application and database.

    Returns:
        HealthResponse with status of the app and database connectivity.
    """
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        db_status = "disconnected"
        logger.warning("Database health check failed: %s", e)

    overall = "healthy" if db_status == "connected" else "unhealthy"

    return HealthResponse(
        status=overall,
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        database=db_status,
    )
