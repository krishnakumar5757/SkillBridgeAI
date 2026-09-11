"""CSP Route for SkillBridge Module 4.

Exposes:
    POST /api/v1/csp/solve
    {
        "student_id": "student-001",
        "role_id": "data_analyst"
    }

Returns the CSP + Backtracking search result.
"""

from fastapi import APIRouter, Depends, Query
from typing import Any

from app.core.database import get_db
from app.services.csp_service import solve_csp

router = APIRouter(prefix="/api/v1/csp", tags=["CSP"])


@router.post("/solve", response_model=dict[str, Any])
def csp_solve(
    student_id: str = Query(..., description="Student identifier"),
    role_id: str = Query(..., description="Target career role identifier"),
    db: Any = Depends(get_db),
) -> Any:
    """Run CSP + Backtracking search to find a valid learning path.

    Given a student's current skills and a target career role,
    finds a valid assignment of proficiency levels to skills the
    student needs to learn, respecting prerequisites, required
    skills, and other constraints via backtracking search.

    Returns:
        - success: whether a valid assignment was found
        - ordered_selected_skills: skills in valid learning order
        - assignments: skill_name -> assigned proficiency
        - constraints_checked: total constraint checks during search
        - backtrack_count: number of backtracks performed
        - failure_reason: why the search failed (if applicable)
        - algorithm: "CSP Backtracking with MRV"
    """
    result = solve_csp(student_id, role_id, db=db)
    return result