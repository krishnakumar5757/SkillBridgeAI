"""
SkillBridge AI — Database Configuration

SQLAlchemy 2.0 engine, session management, and declarative base.
Uses SQLite for development (configurable via DATABASE_URL).
"""

import logging
from collections.abc import Generator
from urllib.parse import urlparse, urlunparse

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger("app.core.database")


# ---------------------------------------------------------------------------
# Database URL Redaction (safe logging)
# ---------------------------------------------------------------------------
def redact_db_url(url: str) -> str:
    """Redact credentials from a database URL for safe logging.

    Any userinfo (username and/or password) is replaced with ``***`` so the
    URL can be logged without leaking credentials. URLs without userinfo
    (e.g. SQLite paths) are returned unchanged.

    Examples:
        postgresql+psycopg2://user:pass@localhost:5432/db
            -> postgresql+psycopg2://***@localhost:5432/db
        postgresql+psycopg2://user@localhost/db
            -> postgresql+psycopg2://***@localhost/db
        sqlite:///./skillbridge.db
            -> sqlite:///./skillbridge.db
    """
    if "://" not in url:
        return url
    parsed = urlparse(url)
    if not parsed.username:
        # No userinfo present — nothing to redact (covers SQLite and any
        # URL without credentials).
        return url
    netloc = "***"
    if parsed.hostname:
        netloc += f"@{parsed.hostname}"
    if parsed.port:
        netloc += f":{parsed.port}"
    return urlunparse(parsed._replace(netloc=netloc))


# ---------------------------------------------------------------------------
# Engine Creation
# ---------------------------------------------------------------------------
_connect_args: dict = {}
_engine_kwargs: dict = {}

if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite needs check_same_thread=False for FastAPI's threaded usage.
    _connect_args = {"check_same_thread": False}
    # Use StaticPool for in-memory SQLite to share connection across threads.
    if ":memory:" in settings.DATABASE_URL:
        from sqlalchemy.pool import StaticPool

        _engine_kwargs = {"poolclass": StaticPool}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    echo=settings.DEBUG,
    **_engine_kwargs,
)


# ---------------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Declarative Base
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""

    pass


# ---------------------------------------------------------------------------
# Dependency — Database Session
# ---------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session per request.

    Usage in routes:
        @router.get("/")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Database Initialization
# ---------------------------------------------------------------------------
def init_db() -> None:
    """Create all tables defined on Base.metadata.

    This is used for development and testing. In production, use Alembic
    migrations instead.

    Note: Business models must be imported before calling this function so
    they are registered on Base.metadata. Module 1-4 model imports will be
    added here as those modules are implemented.
    """
    # Import models here so they are registered on Base.metadata
    # before create_all is called. Uncomment as modules are implemented:
    # from app.models import student, skill, career, roadmap, readiness

    if not Base.metadata.tables:
        logger.warning(
            "init_db() called but no models are registered on Base.metadata. "
            "No tables will be created. Ensure model modules are imported."
        )

    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# Database Connection Check
# ---------------------------------------------------------------------------
def check_db_connection() -> bool:
    """Check that the database is reachable.

    Returns True if the connection is healthy, False otherwise.
    On failure, a safe message is logged at WARNING level (the exception
    type only — never the raw exception, which may contain the database URL
    or credentials). The full traceback is logged at DEBUG level for
    diagnostics, which is disabled in production.
    """
    from sqlalchemy import text

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Database connection check failed: %s", type(exc).__name__)
        logger.debug("Database connection check failure detail:", exc_info=True)
        return False

