"""Career Readiness Route for SkillBridge Module 4.

Exposes:
    POST /api/v1/career-readiness/analyze
    {
        "student_id": "student-001",
        "role_id": "data_analyst"
    }

Returns career readiness analysis with score, level, gaps, strengths,
recommendations, and roadmap context.
"""

from fastapi import APIRouter, Depends, Query
from typing import Any

from app.core.database import get_db
from app.services.career_readiness import analyze_career_readiness

router = APIRouter(prefix="/api/v1/career-readiness", tags=["Career Readiness"])


@router.post("/analyze", response_model=dict[str, Any])
def career_readiness_analyze(
    student_id: str = Query(..., description="Student identifier"),
    role_id: str = Query(..., description="Target career role identifier"),
    db: Any = Depends(get_db),
) -> Any:
    """Analyze a student's readiness for a target career role.

    Evaluates skill coverage, proficiency match, core skill importance,
    and missing/below-required skills to produce a deterministic 0–100
    readiness score with explainable levels and recommendations.

    Returns:
        - readiness_score: int (0–100)
        - readiness_level: str ("Ready"/"Nearly Ready"/"Developing"/"Not Ready")
        - total_required_skills: int
        - skills_met: list of skill summaries meeting requirements
        - skills_missing: list of skill summaries required but absent
        - skills_below: list of skill summaries below required proficiency
        - coverage_percentage: float (0–100)
        - proficiency_percentage: float (0–100)
        - strengths: list of strength descriptions
        - priority_gaps: list of priority gap descriptions
        - recommendations: list of recommendation strings
        - roadmap_summary: A* / CSP learning-plan context where available
        - summary: human-readable explanation
        - algorithm: "Career Readiness Analysis"
    """
    result = analyze_career_readiness(student_id, role_id, db=db)
    return result