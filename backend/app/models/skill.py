"""SkillBridge AI - Skill Models

SQLAlchemy models for skill-related entities: Skill, StudentSkill.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.student import Student


from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseMixin


class Skill(Base, BaseMixin):
    """Canonical skill entity (lookup table)."""

    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Optional: learning_cost_hours, etc.

    # Relationships
    student_skills: Mapped[list[StudentSkill]] = relationship(
        "StudentSkill", back_populates="skill", cascade="all, delete-orphan"
    )


class StudentSkill(Base, BaseMixin):
    """Association between a student and a skill with proficiency and source."""

    __tablename__ = "student_skills"

    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), nullable=False)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id"), nullable=False)
    # Proficiency level: beginner, intermediate, advanced
    proficiency: Mapped[str] = mapped_column(String(20), nullable=False)
    # Source of this skill entry: self_reported, resume, inferred
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    # Confidence score (0.0 to 1.0) for the proficiency assessment
    confidence: Mapped[float] = mapped_column(nullable=False)

    # Relationships
    student: Mapped[Student] = relationship("Student", back_populates="student_skills")
    skill: Mapped[Skill] = relationship("Skill", back_populates="student_skills")

    # Note: We allow multiple rows for the same (student_id, skill_id) with different sources.
    # We handle uniqueness of (student_id, skill_id, source) in the service layer if needed.
