"""
SkillBridge AI — Test Configuration and Fixtures

Provides shared test fixtures including a test database (in-memory SQLite)
and a FastAPI TestClient. Tests run in isolation without affecting the
development database.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db

# Import all models to ensure they are registered with Base before creating tables
from app.models.student import Student, AcademicInfo, Interest, Project, Resume
from app.models.skill import Skill, StudentSkill


# ---------------------------------------------------------------------------
# Test Database Engine (in-memory SQLite)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def test_engine():
    """Create an in-memory SQLite engine for the test session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


# ---------------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def session_factory(test_engine):
    """Session factory bound to the test engine."""
    return sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


# ---------------------------------------------------------------------------
# Database Session Fixture
# ---------------------------------------------------------------------------
@pytest.fixture
def db_session(session_factory):
    """Provide a clean database session for each test."""
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# FastAPI Test Client
# ---------------------------------------------------------------------------
@pytest.fixture
def client(session_factory):
    """Provide a FastAPI TestClient with the test database wired in."""
    from app.main import create_app

    app = create_app()

    # Override the get_db dependency to use the test database
    def override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

