"""
SkillBridge AI — Module 1 Routes

API endpoints for Module 1: Student Intelligence.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.skill import StudentSkill
from app.models.student import Student
from app.schemas.student import (
    AcademicInfoCreateRequest,
    AcademicInfoResponse,
    InterestCreateRequest,
    InterestResponse,
    ProjectCreateRequest,
    ProjectResponse,
    StudentProfileCreateRequest,
    StudentProfileResponse,
    StudentSkillCreateRequest,
    StudentSkillResponse,
)
from app.services.module1 import (
    academic_info_service,
    interest_service,
    profile_service,
    project_service,
    student_skill_service,
)
from app.services.module1.resume_service import ResumeService

resume_service = ResumeService()

router = APIRouter(tags=["module-1"])


# ---------------------------------------------------------------------------
# Student Profile
# ---------------------------------------------------------------------------
@router.post(
    "/profile",
    response_model=StudentProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    profile_in: StudentProfileCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a new student profile."""
    # Check if email already exists
    existing_student = (
        db.query(Student).filter(Student.email == profile_in.email).first()
    )
    if existing_student:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Student with this email already exists",
    )
    student = profile_service.create_profile(db, profile_in)
    return student


@router.get(
    "/profile/{student_id}",
    response_model=StudentProfileResponse,
)
def get_profile(
    student_id: str = Path(..., example="550e8400-e29b-41d4-a716-446655440000"),
    db: Session = Depends(get_db),
):
    """Get a student profile by ID."""
    student = profile_service.get_profile(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    return student


# ---------------------------------------------------------------------------
# Academic Information
# ---------------------------------------------------------------------------
@router.post(
    "/academic-info",
    response_model=AcademicInfoResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_academic_info(
    student_id: str,
    academic_in: AcademicInfoCreateRequest,
    db: Session = Depends(get_db),
):
    """Create academic information for a student."""
    try:
        academic_info = academic_info_service.create_academic_info(
            db, student_id, academic_in
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
    return academic_info


@router.get(
    "/academic-info/{student_id}",
    response_model=list[AcademicInfoResponse],
)
def get_academic_info(
    student_id: str = Path(..., example="550e8400-e29b-41d4-a716-446655440000"),
    db: Session = Depends(get_db),
):
    """Get all academic information records for a student."""
    academic_infos = academic_info_service.get_academic_info_by_student_id(
        db, student_id
    )
    return academic_infos


# ---------------------------------------------------------------------------
# Areas of Interest
# ---------------------------------------------------------------------------
@router.post(
    "/interests",
    response_model=InterestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interest(
    student_id: str,
    interest_in: InterestCreateRequest,
    db: Session = Depends(get_db),
):
    """Create an interest for a student."""
    try:
        interest = interest_service.create_interest(db, student_id, interest_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
    return interest


@router.get(
    "/interests/{student_id}",
    response_model=list[InterestResponse],
)
def get_interests(
    student_id: str = Path(..., example="550e8400-e29b-41d4-a716-446655440000"),
    db: Session = Depends(get_db),
):
    """Get all interests for a student."""
    interests = interest_service.get_interests_by_student_id(db, student_id)
    return interests


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    student_id: str,
    project_in: ProjectCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a project for a student."""
    try:
        project = project_service.create_project(db, student_id, project_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
    return project


@router.get(
    "/projects/{student_id}",
    response_model=list[ProjectResponse],
)
def get_projects(
    student_id: str = Path(..., example="550e8400-e29b-41d4-a716-446655440000"),
    db: Session = Depends(get_db),
):
    """Get all projects for a student."""
    projects = project_service.get_projects_by_student_id(db, student_id)
    return projects


# ---------------------------------------------------------------------------
# Existing Skills (Self-reported)
# ---------------------------------------------------------------------------
@router.post(
    "/skills/self-reported",
    response_model=StudentSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_self_reported_skill(
    student_id: str,
    skill_in: StudentSkillCreateRequest,
    db: Session = Depends(get_db),
):
    """Add a self-reported skill for a student."""
    try:
        student_skill = student_skill_service.add_self_reported_skill(
            db, student_id, skill_in
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
    return student_skill


@router.get(
    "/skills/{student_id}",
    response_model=list[StudentSkillResponse],
)
def get_skills(
    student_id: str = Path(..., example="550e8400-e29b-41d4-a716-446655440000"),
    db: Session = Depends(get_db),
):
    """Get all skills for a student."""
    skills = student_skill_service.get_skills_by_student_id(db, student_id)
    return skills


# ---------------------------------------------------------------------------
# Resume Upload & Processing
# ---------------------------------------------------------------------------
@router.post(
    "/students/{student_id}/resumes/upload",
    status_code=status.HTTP_201_CREATED,
)
def upload_resume(
    student_id: str = Path(..., example="550e8400-e29b-41d4-a716-446655440000"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload and process a resume for a student."""
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )
    try:
        resume = resume_service.upload_resume(db, student_id, file)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
    except Exception as e:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process resume: {e!s}",
        ) from None
    return {
        "resume_id": resume.id,
        "file_name": resume.file_name,
        "status": "processed",
        "message": "Resume uploaded and skills extracted successfully",
    }


# Optional endpoints for retrieving resume data (for debugging/demo)
@router.get(
    "/resumes/{student_id}",
)
def get_resume(
    student_id: str = Path(..., example="550e8400-e29b-41d4-a716-446655440000"),
    db: Session = Depends(get_db),
):
    """Get resume metadata for a student."""
    resume = resume_service.get_resume(db, student_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No resume found for student {student_id}",
        )
    return {
        "resume_id": resume.id,
        "file_name": resume.file_name,
        "file_size": resume.file_size,
        "mime_type": resume.mime_type,
        "upload_date": resume.created_at,
    }


@router.get(
    "/resumes/{student_id}/text",
)
def get_resume_text(
    student_id: str = Path(..., example="550e8400-e29b-41d4-a716-446655440000"),
    db: Session = Depends(get_db),
):
    """Get extracted text from a student's resume."""
    text = resume_service.get_resume_text(db, student_id)
    if text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No extracted text found for student {student_id}",
        )
    return {"extracted_text": text}


@router.get(
    "/resumes/{student_id}/skills",
)
def get_resume_skills(
    student_id: str = Path(..., example="550e8400-e29b-41d4-a716-446655440000"),
    db: Session = Depends(get_db),
):
    """Get skills extracted from a student's resume."""
    # Get all resume-derived skills for the student
    skills = (
        db.query(StudentSkill)
        .filter(
            StudentSkill.student_id == student_id,
            StudentSkill.source == "resume",
        )
        .all()
    )
    # Convert to list of dicts
    return [
        {
            "skill_id": skill.skill_id,
            "skill_name": skill.skill.name,
            "category": skill.skill.category,
            "proficiency": skill.proficiency,
            "confidence": skill.confidence,
        }
        for skill in skills
    ]
