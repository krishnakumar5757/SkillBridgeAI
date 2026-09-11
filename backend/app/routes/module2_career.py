"""
SkillBridge AI — Module 2 Routes

API endpoints for Module 2: Career Intelligence.
Provides career role selection and skill gap analysis.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.module2_career import (
    analyze_skill_gap,
    generate_skill_gap_report,
    get_role_skills,
)

router = APIRouter(tags=["module-2"])


# ---------------------------------------------------------------------------
# Career Role Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/career-roles",
)
def list_career_roles() -> dict[str, Any]:
    """List all available career roles.

    Returns:
        Dictionary containing list of role summaries with required skills.
    """
    import json
    from pathlib import Path

    roles_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "roles" / "roles.json"
    if not roles_path.exists():
        return {
            "roles": [],
            "total": 0,
        }

    with open(roles_path, encoding="utf-8") as f:
        roles = json.load(f)

    role_summaries = []
    for role in roles:
        role_summaries.append(
            {
                "id": role["id"],
                "name": role["name"],
                "description": role["description"],
                "category": role["category"],
                "required_skill_count": len(role["required_skills"]),
                "critical_skills": sum(
                    1 for s in role["required_skills"] if s.get("priority") == "critical"
                ),
                "core_skills": sum(1 for s in role["required_skills"] if s.get("is_core", False)),
            }
        )

    return {
        "roles": role_summaries,
        "total": len(role_summaries),
    }


@router.get(
    "/career-roles/{role_id}",
)
def get_career_role(
    role_id: str = Path(..., example="software_engineer"),
) -> dict[str, Any]:
    """Get details for a specific career role.

    Args:
        role_id: The role identifier (software_engineer, data_analyst, frontend_developer).

    Returns:
        Role details including required skills and structure.
    """
    import json
    from pathlib import Path

    roles_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "roles" / "roles.json"
    if not roles_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career roles data not found",
        )

    with open(roles_path, encoding="utf-8") as f:
        roles = json.load(f)

    for role in roles:
        if role["id"] == role_id:
            # Compute skill priority breakdown
            priority_breakdown = {}
            for req in role["required_skills"]:
                p = req.get("priority", "important")
                priority_breakdown[p] = priority_breakdown.get(p, 0) + 1

            return {
                "id": role["id"],
                "name": role["name"],
                "description": role["description"],
                "category": role["category"],
                "required_skills": role["required_skills"],
                "priority_breakdown": priority_breakdown,
                "total_required_skills": len(role["required_skills"]),
                "core_skill_count": sum(1 for s in role["required_skills"] if s.get("is_core", False)),
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Career role '{role_id}' not found",
    )


# ---------------------------------------------------------------------------
# Skill Gap Analysis Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/skill-gap/analyze",
    response_model=dict[str, Any],
)
def analyze_skill_gap_endpoint(
    student_id: str = Query(..., example="student-profile-id"),
    role_id: str = Query(..., example="software_engineer"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Analyze skill gaps for a student against a career role.

    Compares the student's current skills and proficiencies against the
    selected career role's required skills and produces a detailed gap report.

    Args:
        student_id: The student's unique identifier.
        role_id: The target career role identifier.
        db: Database session.

    Returns:
        Comprehensive skill gap analysis including matched strong/weak/missing
        skills, coverage percentages, and prioritized gaps.
    """
    try:
        report = analyze_skill_gap(db, student_id, role_id)
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/skill-gap/report",
    response_model=dict[str, Any],
)
def generate_skill_gap_report_endpoint(
    student_id: str = Query(..., example="student-profile-id"),
    role_id: str = Query(..., example="software_engineer"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Generate a full skill gap report for a student against a career role.

    Convenience endpoint that returns the complete analysis report suitable
    for display in the frontend.

    Args:
        student_id: The student's unique identifier.
        role_id: The target career role identifier.
        db: Database session.

    Returns:
        Full skill gap report with all analysis data.
    """
    try:
        report = generate_skill_gap_report(db, student_id, role_id)
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )