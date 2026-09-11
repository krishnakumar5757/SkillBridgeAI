"""
SkillBridge AI — Base ORM Model

Provides a shared base model class with common fields (id, created_at,
updated_at) that all business entity models can inherit from.

This establishes the model convention for the project. Actual business
entities (Student, Skill, CareerRole, etc.) will be added during their
respective module implementation phases.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column


def _generate_uuid() -> str:
    """Generate a UUID4 string for primary keys."""
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


@declarative_mixin
class BaseMixin:
    """Mixin providing common columns for all entity models.

    Decorated with @declarative_mixin so SQLAlchemy 2.0 correctly
    recognizes it as a mixin and applies its columns to consuming models.

    All business models should inherit from both Base and BaseMixin:
        class Student(Base, BaseMixin):
            __tablename__ = "students"
            ...
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=_generate_uuid,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )
