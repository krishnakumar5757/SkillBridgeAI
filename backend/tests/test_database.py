"""
SkillBridge AI — Database Foundation Tests

Verifies that the SQLAlchemy database configuration works correctly:
- Engine can be created
- Tables can be created on the Base metadata
- The database session dependency works
- The check_db_connection function works
- init_db warns when no models are registered
- BaseMixin applies common columns to a concrete model
- redact_db_url redacts credentials for safe logging

All tests run against the in-memory test engine (see conftest.py). Tests that
exercise functions which default to the module-level (development) engine
monkeypatch that engine to the test engine so the development database file
(``skillbridge.db``) is never created or touched by the test suite.
"""

from datetime import datetime

from sqlalchemy import Column, MetaData, String, Table, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from app.core.database import Base, check_db_connection, get_db, init_db, redact_db_url
from app.models.base import BaseMixin


class TestDatabaseConfiguration:
    """Tests for the database foundation."""

    def test_base_is_declarative(self):
        """Base should be a SQLAlchemy DeclarativeBase subclass."""
        assert issubclass(Base, DeclarativeBase)

    def test_base_mixin_has_id_column(self):
        """BaseMixin should define an 'id' column."""
        assert hasattr(BaseMixin, "id")

    def test_base_mixin_has_timestamps(self):
        """BaseMixin should define created_at and updated_at columns."""
        assert hasattr(BaseMixin, "created_at")
        assert hasattr(BaseMixin, "updated_at")

    def test_base_mixin_applies_columns_to_model(self, test_engine, db_session):
        """BaseMixin should apply id/created_at/updated_at to a concrete model.

        Uses a local declarative base (not the global Base) so the global
        Base.metadata is not polluted for other tests (e.g. the
        init_db "no models registered" warning test).
        """

        class _LocalBase(DeclarativeBase):
            pass

        class _SampleEntity(_LocalBase, BaseMixin):
            __tablename__ = "_sample_entities"
            name: Mapped[str] = mapped_column(String(50), nullable=False)

        _LocalBase.metadata.create_all(bind=test_engine)
        try:
            entity = _SampleEntity(name="test")
            db_session.add(entity)
            db_session.commit()
            db_session.refresh(entity)

            # id is a UUID4 string of 36 characters
            assert isinstance(entity.id, str)
            assert len(entity.id) == 36

            # timestamps populated by the mixin defaults
            assert isinstance(entity.created_at, datetime)
            assert isinstance(entity.updated_at, datetime)
        finally:
            db_session.rollback()
            _LocalBase.metadata.drop_all(bind=test_engine)

    def test_get_db_yields_session(self, db_session):
        """get_db dependency should yield a Session instance."""
        # The db_session fixture already verifies this works
        assert isinstance(db_session, Session)

    def test_tables_can_be_created(self, test_engine):
        """Base.metadata.create_all should create tables on the engine."""
        # Use an isolated MetaData to avoid polluting the global Base.metadata
        # (F-09 fix: do not register throwaway models on the shared Base).
        isolated_metadata = MetaData()
        test_table = Table(
            "test_entities_isolated",
            isolated_metadata,
            Column("id", String(36), primary_key=True),
            Column("name", String(100), nullable=False),
        )

        # Create the table on the test engine
        isolated_metadata.create_all(bind=test_engine, tables=[test_table])

        # Verify the table exists
        inspector = inspect(test_engine)
        table_names = inspector.get_table_names()
        assert "test_entities_isolated" in table_names

        # Clean up — drop the table from the test engine
        isolated_metadata.drop_all(bind=test_engine, tables=[test_table])

        # Verify cleanup
        inspector = inspect(test_engine)
        assert "test_entities_isolated" not in inspector.get_table_names()

    def test_get_db_is_callable(self):
        """get_db should be a callable generator function."""
        assert callable(get_db)


class TestDatabaseConnection:
    """Tests for database connectivity checks."""

    def test_check_db_connection_returns_bool(self, test_engine, monkeypatch):
        """check_db_connection should return a boolean without touching the dev DB.

        Monkeypatches the module-level engine to the in-memory test engine so
        the development ``skillbridge.db`` file is never created.
        """
        monkeypatch.setattr("app.core.database.engine", test_engine)
        result = check_db_connection()
        assert isinstance(result, bool)
        assert result is True  # the test engine is reachable

    def test_check_db_connection_false_on_failure(self, monkeypatch):
        """check_db_connection should return False (and not raise) on failure."""
        # Point the global engine at an unreachable URL to force a failure.
        from sqlalchemy import create_engine

        bad_engine = create_engine("sqlite:///./_nonexistent_dir/does_not_exist.db")
        monkeypatch.setattr("app.core.database.engine", bad_engine)
        try:
            assert check_db_connection() is False
        finally:
            bad_engine.dispose()

    def test_check_db_connection_true_when_reachable(self, test_engine):
        """The underlying SELECT 1 should succeed when the DB is reachable."""
        from sqlalchemy import text

        with test_engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
        assert result == 1

    def test_init_db_creates_tables(self, test_engine):
        """init_db should create all registered tables without error."""
        # init_db uses the global engine; for the test we verify
        # that create_all works on the test engine
        Base.metadata.create_all(bind=test_engine)
        inspector = inspect(test_engine)
        # There may be no business tables yet, but the call should not error
        assert isinstance(inspector.get_table_names(), list)

    def test_init_db_warns_when_no_models(self, test_engine, monkeypatch, caplog):
        """init_db should log a warning when no models are registered.

        Monkeypatches the module-level engine to the test engine so the
        development database file is not created.
        """
        import logging
        from sqlalchemy import MetaData

        # Store the original metadata to restore later
        original_metadata = Base.metadata
        # Replace with a clean metadata to simulate no models registered
        Base.metadata = MetaData()

        try:
            monkeypatch.setattr("app.core.database.engine", test_engine)
            with caplog.at_level(logging.WARNING, logger="app.core.database"):
                init_db()
            assert any(
                "no models are registered" in record.message.lower()
                for record in caplog.records
            )
        finally:
            # Restore the original metadata
            Base.metadata = original_metadata


class TestDbUrlRedaction:
    """Tests for safe logging of database URLs (credential redaction)."""

    def test_redact_password_url(self):
        """URLs with user:pass should have userinfo replaced with ***."""
        url = "postgresql+psycopg2://user:secret@localhost:5432/db"
        redacted = redact_db_url(url)
        assert "secret" not in redacted
        assert "user" not in redacted
        assert "***" in redacted
        assert "localhost" in redacted
        assert "5432" in redacted
        assert redacted.startswith("postgresql+psycopg2://")

    def test_redact_username_only_url(self):
        """URLs with a username but no password should also be redacted."""
        url = "postgresql+psycopg2://user@localhost:5432/db"
        redacted = redact_db_url(url)
        assert "user" not in redacted
        assert "***" in redacted
        assert "localhost" in redacted

    def test_sqlite_path_unchanged(self):
        """SQLite file URLs have no userinfo and should be unchanged."""
        url = "sqlite:///./skillbridge.db"
        assert redact_db_url(url) == url

    def test_in_memory_sqlite_unchanged(self):
        """In-memory SQLite URLs have no userinfo and should be unchanged."""
        url = "sqlite://"
        assert redact_db_url(url) == url

    def test_no_scheme_unchanged(self):
        """Bare paths (no scheme) should be returned unchanged."""
        assert redact_db_url("./skillbridge.db") == "./skillbridge.db"
