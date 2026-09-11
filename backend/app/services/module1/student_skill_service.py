"""
SkillBridge AI — Student Skill Service

Service for managing student skills (self-reported and resume-derived).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.skill import Skill, StudentSkill
from app.models.student import Student
from app.schemas.student import StudentSkillCreateRequest


def add_self_reported_skill(
    db: Session, student_id: str, skill_in: StudentSkillCreateRequest
) -> StudentSkill:
    """Add a self-reported skill for a student."""
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError(f"Student with id {student_id} not found")
    # Verify skill exists
    skill = db.query(Skill).filter(Skill.id == skill_in.skill_id).first()
    if not skill:
        raise ValueError(f"Skill with id {skill_in.skill_id} not found")

    # For self-reported skills, source is always 'self_reported'
    # Confidence can be provided or default to 1.0 (full confidence in self-report)
    # However, the schema does not include confidence in the create request.
    # We'll set confidence to 1.0 for self-reported skills as per the plan?
    # The plan says: proficiency validation and source tracking.
    # We'll set confidence to 1.0 for self-reported skills.
    db_student_skill = StudentSkill(
        student_id=student_id,
        skill_id=skill_in.skill_id,
        proficiency=skill_in.proficiency,
        source="self_reported",
        confidence=1.0,  # Full confidence in self-reported skills
    )
    db.add(db_student_skill)
    db.commit()
    db.refresh(db_student_skill)
    return db_student_skill


def add_resume_skill(
    db: Session,
    student_id: str,
    skill_id: str,
    proficiency: str = "beginner",
    confidence: float = 0.8,
) -> StudentSkill:
    """Add a resume-derived skill for a student."""
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError(f"Student with id {student_id} not found")
    # Verify skill exists
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise ValueError(f"Skill with id {skill_id} not found")
# Validate proficiency
    if proficiency not in ("beginner", "intermediate", "advanced"):
        raise ValueError(
            f"Invalid proficiency level: {proficiency}. "
            "Must be 'beginner', 'intermediate', or 'advanced'"
        )
    # Validate confidence
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"Confidence must be between 0.0 and 1.0, got {confidence}")

    db_student_skill = StudentSkill(
        student_id=student_id,
        skill_id=skill_id,
        proficiency=proficiency,
        source="resume",
        confidence=confidence,
    )
    db.add(db_student_skill)
    db.commit()
    db.refresh(db_student_skill)
    return db_student_skill


def delete_resume_skills_for_student(db: Session, student_id: str) -> int:
    """Delete all resume-derived skills for a student.
    Returns the number of skills deleted.
    """
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError(f"Student with id {student_id} not found")

    # Delete skills with source = 'resume' for this student
    deleted_count = (
        db.query(StudentSkill)
        .filter(
            StudentSkill.student_id == student_id,
            StudentSkill.source == "resume",
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted_count


def get_skills_by_student_id(
    db: Session, student_id: str
) -> list[StudentSkill]:
    """Get all skills for a student."""
    return (
        db.query(StudentSkill)
        .filter(StudentSkill.student_id == student_id)
        .order_by(StudentSkill.created_at.asc())
        .all()
    )


def get_skill_by_id(
    db: Session, student_skill_id: str
) -> StudentSkill | None:
    """Get a student skill by ID."""
    return (
        db.query(StudentSkill)
        .filter(StudentSkill.id == student_skill_id)
        .first()
    )


def delete_skill(db: Session, student_skill_id: str) -> bool:
    """Delete a student skill by ID."""
    db_skill = get_skill_by_id(db, student_skill_id)
    if db_skill:
        db.delete(db_skill)
        db.commit()
        return True
    return False
