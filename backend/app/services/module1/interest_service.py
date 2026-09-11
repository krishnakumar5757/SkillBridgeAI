"""
SkillBridge AI — Interest Service

Service for managing student interests.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.student import Interest, Student
from app.schemas.student import InterestCreateRequest


def create_interest(
    db: Session, student_id: str, interest_in: InterestCreateRequest
) -> Interest:
    """Create an interest for a student."""
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError(f"Student with id {student_id} not found")

    db_interest = Interest(
        student_id=student_id,
        name=interest_in.name,
    )
    db.add(db_interest)
    db.commit()
    db.refresh(db_interest)
    return db_interest


def get_interests_by_student_id(
    db: Session, student_id: str
) -> list[Interest]:
    """Get all interests for a student."""
    return (
        db.query(Interest)
        .filter(Interest.student_id == student_id)
        .order_by(Interest.created_at.asc())
        .all()
    )


def get_interest_by_id(
    db: Session, interest_id: str
) -> Interest | None:
    """Get an interest by ID."""
    return (
        db.query(Interest)
        .filter(Interest.id == interest_id)
        .first()
    )


def delete_interest(db: Session, interest_id: str) -> bool:
    """Delete an interest by ID."""
    db_interest = get_interest_by_id(db, interest_id)
    if db_interest:
        db.delete(db_interest)
        db.commit()
        return True
    return False
