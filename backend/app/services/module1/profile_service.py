"""
SkillBridge AI — Profile Service

Service for managing student profiles.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.student import StudentProfileCreateRequest


def create_profile(db: Session, profile_in: StudentProfileCreateRequest) -> Student:
    """Create a new student profile."""
    db_student = Student(
        first_name=profile_in.first_name,
        last_name=profile_in.last_name,
        email=profile_in.email,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_profile(db: Session, student_id: str) -> Student | None:
    """Get a student profile by ID."""
    return db.query(Student).filter(Student.id == student_id).first()
