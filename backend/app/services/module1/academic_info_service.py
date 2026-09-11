"""
SkillBridge AI — Academic Info Service

Service for managing student academic information.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.student import AcademicInfo, Student
from app.schemas.student import AcademicInfoCreateRequest


def create_academic_info(
    db: Session, student_id: str, academic_in: AcademicInfoCreateRequest
) -> AcademicInfo:
    """Create academic information for a student."""
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError(f"Student with id {student_id} not found")

    db_academic_info = AcademicInfo(
        student_id=student_id,
        institution=academic_in.institution,
        degree=academic_in.degree,
        major=academic_in.major,
        graduation_year=academic_in.graduation_year,
        gpa=academic_in.gpa,
    )
    db.add(db_academic_info)
    db.commit()
    db.refresh(db_academic_info)
    return db_academic_info


def get_academic_info_by_student_id(
    db: Session, student_id: str
) -> list[AcademicInfo]:
    """Get all academic information records for a student."""
    return (
        db.query(AcademicInfo)
        .filter(AcademicInfo.student_id == student_id)
        .order_by(AcademicInfo.created_at.desc())
        .all()
    )


def get_academic_info_by_id(
    db: Session, academic_info_id: str
) -> AcademicInfo | None:
    """Get an academic information record by ID."""
    return (
        db.query(AcademicInfo)
        .filter(AcademicInfo.id == academic_info_id)
        .first()
    )
