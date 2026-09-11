"""
SkillBridge AI — Project Service

Service for managing student projects.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.student import Project, Student
from app.schemas.student import ProjectCreateRequest


def create_project(
    db: Session, student_id: str, project_in: ProjectCreateRequest
) -> Project:
    """Create a project for a student."""
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError(f"Student with id {student_id} not found")

    db_project = Project(
        student_id=student_id,
        title=project_in.title,
        description=project_in.description,
        technologies=project_in.technologies,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_projects_by_student_id(
    db: Session, student_id: str
) -> list[Project]:
    """Get all projects for a student."""
    return (
        db.query(Project)
        .filter(Project.student_id == student_id)
        .order_by(Project.created_at.asc())
        .all()
    )


def get_project_by_id(
    db: Session, project_id: str
) -> Project | None:
    """Get a project by ID."""
    return (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )


def delete_project(db: Session, project_id: str) -> bool:
    """Delete a project by ID."""
    db_project = get_project_by_id(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False
