"""
SkillBridge AI — Module 3 Routes

API endpoints for Module 3: Learning Intelligence.
Provides A* Learning Roadmap generation.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.module3_learning import generate_learning_roadmap

router = APIRouter(tags=["module-3"])


# ---------------------------------------------------------------------------
# Learning Roadmap Endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/learning-roadmap/generate",
    response_model=dict[str, Any],
)
def generate_learning_roadmap_endpoint(
    student_id: str = Query(..., example="student-profile-id"),
    role_id: str = Query(..., example="software_engineer"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Generate a personalized learning roadmap using A* Search.

    Compares the student's current skills against the selected career role's
    required skills and uses A* Search to find the minimum-cost learning path
    from the student's current skill state to the target role's required skill state.

    The A* algorithm uses f(n) = g(n) + h(n) where:
    - g(n) = accumulated learning cost from the student's current state
    - h(n) = estimated remaining cost to reach the target role (admissible heuristic)
    - f(n) = total estimated cost

    The algorithm searches through skill-learning states, expanding the lowest
    f-score node, and reconstructs the optimal path to the goal.

    Args:
        student_id: The student's unique identifier.
        role_id: The target career role identifier.
        db: Database session.

    Returns:
        Dictionary containing:
        - roadmap: Ordered list of learning steps
        - total_estimated_cost: Total estimated learning cost
        - nodes_expanded: Number of nodes expanded during search
        - search_depth: Depth of the search tree
        - goal_reached: Whether the target state was achieved
        - algorithm: Algorithm identifier string

    Raises:
        HTTPException: If student or role is not found, or on integration failure.
    """
    try:
        result = generate_learning_roadmap(student_id=student_id, role_id=role_id, db=db)
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate learning roadmap: {e!s}",
        )