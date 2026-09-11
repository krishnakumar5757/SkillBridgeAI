"""SkillBridge AI - Student Models

SQLAlchemy models for student-related entities: Student, Resume, Project.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseMixin
from app.models.skill import StudentSkill


class Student(Base, BaseMixin):
    """Student entity representing a user of the system."""

    __tablename__ = "students"

    # Personal information
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    # Optional: phone number, date of birth, etc. can be added later

    # Relationships
    resume: Mapped[Resume | None] = relationship(
        "Resume", back_populates="student", uselist=False, cascade="all, delete-orphan"
    )
    academic_infos: Mapped[list[AcademicInfo]] = relationship(
        "AcademicInfo", back_populates="student", cascade="all, delete-orphan"
    )
    interests: Mapped[list[Interest]] = relationship(
        "Interest", back_populates="student", cascade="all, delete-orphan"
    )
    projects: Mapped[list[Project]] = relationship(
        "Project", back_populates="student", cascade="all, delete-orphan"
    )
    student_skills: Mapped[list[StudentSkill]] = relationship(
        "StudentSkill", back_populates="student", cascade="all, delete-orphan"
    )


class Resume(Base, BaseMixin):
    """Resume file uploaded by a student."""

    __tablename__ = "resumes"

    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), nullable=False)
    # File metadata
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)  # stored path
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Extracted text (for reprocessing without re-upload)
    extracted_text: Mapped[Text | None] = mapped_column(Text, nullable=True)

    # Relationship
    student: Mapped[Student] = relationship("Student", back_populates="resume")


class Project(Base, BaseMixin):
    """Project undertaken by a student."""

    __tablename__ = "projects"

    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Text | None] = mapped_column(Text, nullable=True)
    technologies: Mapped[Text | None] = mapped_column(Text, nullable=True)
    # comma-separated or JSON
    # Optional: start_date, end_date, url, etc.

    # Relationship
    student: Mapped[Student] = relationship("Student", back_populates="projects")


# Note: AcademicInfo and Interest models will be in this file as well?
# According to the Development Structure, they are in student.py?
# Actually, the Development Structure shows student.py contains Student, Resume, Project.
# AcademicInfo and Interest are not listed. But we need them for Module 1.
# Let's check the Development Structure again:
# it only shows the model files, not the exact contents.
# We'll put AcademicInfo and Interest in this file for now, but note that the Development Structure
# does not forbid having multiple models in one file. However, to keep it clean, we might want to
# separate them. But the example shows one file per
# domain (student, skill, career, roadmap, readiness).
# AcademicInfo and Interest are part of the student domain, so we can put them in student.py.

class AcademicInfo(Base, BaseMixin):
    """Academic information of a student."""

    __tablename__ = "academic_infos"

    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), nullable=False)
    institution: Mapped[str] = mapped_column(String(200), nullable=False)
    degree: Mapped[str] = mapped_column(String(100), nullable=False)
    major: Mapped[str | None] = mapped_column(String(100), nullable=True)
    graduation_year: Mapped[Integer | None] = mapped_column(Integer, nullable=True)
    gpa: Mapped[float | None] = mapped_column(nullable=True)  # GPA on 4.0 scale

    # Relationship
    student: Mapped[Student] = relationship("Student", back_populates="academic_infos")


class Interest(Base, BaseMixin):
    """Area of interest for a student."""

    __tablename__ = "interests"

    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Optional: category, description, etc.

    # Relationship
    student: Mapped[Student] = relationship("Student", back_populates="interests")



