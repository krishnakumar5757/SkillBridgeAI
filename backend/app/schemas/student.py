"""
SkillBridge AI — Student Schemas

Pydantic schemas for student-related entities: student profile, academic info,
interests, projects, and student skills.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Student Profile
# ---------------------------------------------------------------------------
class StudentProfileCreateRequest(BaseModel):
    """Request to create a student profile."""

    first_name: str = Field(..., max_length=50, example="John")
    last_name: str = Field(..., max_length=50, example="Doe")
    email: str = Field(..., max_length=120, example="john.doe@example.com")


class StudentProfileResponse(BaseModel):
    """Response for a student profile."""

    id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Academic Information
# ---------------------------------------------------------------------------
class AcademicInfoCreateRequest(BaseModel):
    """Request to create academic information."""

    institution: str = Field(..., max_length=200, example="University of Example")
    degree: str = Field(..., max_length=100, example="Bachelor of Science")
    major: str | None = Field(None, max_length=100, example="Computer Science")
    graduation_year: int | None = Field(None, example=2025)
    gpa: float | None = Field(None, ge=0.0, le=4.0, example=3.5)


class AcademicInfoResponse(BaseModel):
    """Response for academic information."""

    id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440001")
    student_id: str
    institution: str
    degree: str
    major: str | None
    graduation_year: int | None
    gpa: float | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Areas of Interest
# ---------------------------------------------------------------------------
class InterestCreateRequest(BaseModel):
    """Request to create an area of interest."""

    name: str = Field(..., max_length=100, example="Artificial Intelligence")


class InterestResponse(BaseModel):
    """Response for an area of interest."""

    id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440002")
    student_id: str
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
class ProjectCreateRequest(BaseModel):
    """Request to create a project."""

    title: str = Field(..., max_length=200, example="Smart Home Automation")
    description: str | None = Field(None, example="A system to automate home appliances.")
    technologies: str | None = Field(None, example="Python, Arduino, IoT")


class ProjectResponse(BaseModel):
    """Response for a project."""

    id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440003")
    student_id: str
    title: str
    description: str | None
    technologies: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Existing Skills (Self-reported)
# ---------------------------------------------------------------------------
class StudentSkillCreateRequest(BaseModel):
    """Request to add a self-reported skill."""

    skill_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440004")
    proficiency: str = Field(
        ..., pattern="^(beginner|intermediate|advanced)$", example="intermediate"
    )
    # Note: source is implicitly self_reported for this endpoint
    # confidence: Optional[float] = Field(None, ge=0.0, le=1.0, example=0.8)


class StudentSkillResponse(BaseModel):
    """Response for a student skill."""

    id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440005")
    student_id: str
    skill_id: str
    proficiency: str
    source: str
    confidence: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Student Skill Profile (for Phase 2+)
# ---------------------------------------------------------------------------
# Note: This will be implemented in later phases when we merge resume and self-reported skills.
class StudentSkillProfileResponse(BaseModel):
    """Response for a student's skill profile (merged skills)."""

    student_id: str
    skills: list[StudentSkillResponse]
    last_updated: datetime

    class Config:
        from_attributes = True

