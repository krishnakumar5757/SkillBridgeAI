"""
SkillBridge AI — FastAPI Application Entry Point

Initializes the FastAPI application with:
- CORS middleware (configured for the frontend origin)
- Exception handlers (consistent error format)
- Router includes (health check + future module routers)
- Logging configuration
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import JWT_SECRET_MIN_LENGTH, settings
from app.core.database import redact_db_url
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.routes.health import router as health_router
from app.routes.module1_student import router as module1_student_router
from app.routes.module2_career import router as module2_career_router
from app.routes.module3_learning import router as module3_learning_router
from app.routes.csp import router as csp_router
from app.routes.career_readiness import router as career_readiness_router


# ---------------------------------------------------------------------------
# Application Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger = get_logger("app.main")
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Database URL: %s", redact_db_url(settings.DATABASE_URL))
    logger.info("LLM enabled: %s", settings.ENABLE_LLM)

    # Security check: refuse to start with an insecure JWT secret in non-debug mode
    if not settings.DEBUG and settings.is_jwt_secret_insecure:
        raise RuntimeError(
            "JWT_SECRET is insecure (placeholder or shorter than "
            f"{JWT_SECRET_MIN_LENGTH} characters). "
            "Set a strong secret in .env before running in non-debug mode."
        )
    if settings.DEBUG and settings.is_jwt_secret_insecure:
        logger.warning(
            "JWT_SECRET is insecure (placeholder or short). "
            "This is acceptable for local development only."
        )


    yield

    logger.info("Shutting down %s", settings.APP_NAME)


# ---------------------------------------------------------------------------
# FastAPI App Creation
# ---------------------------------------------------------------------------
def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Configure logging
    setup_logging(debug=settings.DEBUG)

    # Create the app
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Intelligent Skill Gap and Career Readiness Assessment System. "
            "Analyzes student skills, identifies gaps against career roles, "
            "generates personalized learning roadmaps, and evaluates career readiness."
        ),
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    # CORS middleware — allow the configured frontend origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Include routers
    app.include_router(health_router)
    app.include_router(module1_student_router, prefix="/api/v1")
    app.include_router(module2_career_router, prefix="/api/v1")
    app.include_router(module3_learning_router, prefix="/api/v1")
    app.include_router(csp_router)
    app.include_router(career_readiness_router, prefix="/api/v1")

    # Future module routers will be included here:
    # from app.routes import auth, module1_student, module2_career, ...
    # app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    # app.include_router(module1_student.router, prefix="/api/v1", tags=["module-1"])
    # etc.

    return app


# Module-level app instance for uvicorn
app = create_app()