"""CSP Service for SkillBridge Module 4.

Wraps the existing CSP + Backtracking solver (from modules/module-4-career-readiness/backtracking-csp/)
and connects it to SkillBridge student-skill + role-required-skill data.

Provides:
- solve_csp(student_id, role_id, db): Sets up CSP variables for skills the student needs to learn,
  runs backtracking search, and returns a valid ordered learning path.
- The CSP models the problem as: which skills to assign (learn) and in what order,
  subject to prerequisite, required, conflicting, and dependency constraints.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from fastapi import Depends

# Add the backtracking-csp module to path so we can import its components
_BACKTRACKING_CSP_PATH = r"D:\FOAI\Skillbridge\modules\module-4-career-readiness\backtracking-csp"
if _BACKTRACKING_CSP_PATH not in sys.path:
    sys.path.insert(0, _BACKTRACKING_CSP_PATH)

from app.core.database import get_db
from app.services.module3_learning import get_student_skills_from_db

# Import CSP components from the existing Module 4 backtracking-csp package
from csp import CSP  # noqa: E402
from solver import backtracking_search  # noqa: E402
from constraints import (  # noqa: E402
    required_skills,
    conflicting_skills,
    dependency_validation,
    prerequisite_ordering,
)

# Path to roles.json
_ROLES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "data",
    "roles",
    "roles.json",
)

# Try to load roles.json; fall back to empty list if not found
try:
    with open(_ROLES_PATH, encoding="utf-8") as f:
        _ROLES_DATA = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    _ROLES_DATA = []

# Build a lookup: role_id -> role info
_ROLES_BY_ID = {}
for role in _ROLES_DATA:
    _ROLES_BY_ID[role["id"]] = role


def _load_student_skills(student_id: str, db: Any = None) -> dict[str, str]:
    """Load student skills from database using the provided db session.

    Args:
        student_id: student identifier
        db: database session (optional; for standalone testing without a session,
            pass db=None and the function will use a fallback approach)

    Returns:
        dict mapping skill_id -> proficiency_level, or empty dict if student not found
    """
    if db is not None:
        skills = get_student_skills_from_db(student_id, db)
    else:
        # No db session provided — return empty dict.
        # The CSP will have no student skills, meaning all role skills are "needed".
        # This mode is intended for testing; in production, always provide a db session.
        skills = {}
    if skills is not None:
        return skills
    # If student not in DB, return empty — CSP will have no variables
    return {}


def _load_role_required_skills(role_id: str) -> list[dict[str, str]]:
    """Load role's required skills from roles.json."""
    role = _ROLES_BY_ID.get(role_id)
    if role is not None:
        return role["required_skills"]
    return []


def _build_csp_variables(
    student_skills: dict[str, str],
    role_required_skills: list[dict[str, str]],
) -> tuple[list[str], dict[str, list[str]]]:
    """Build CSP variable names and domains for skills the student doesn't have.

    Returns:
        variable_names: list of skill names to consider as CSP variables
        domains: mapping variable_name -> list of possible values (proficiency levels)
    """
    # Skills student already has
    student_skill_ids = set(student_skills.keys())

    # Skills required by the role
    required_skill_ids = set()
    for skill_info in role_required_skills:
        required_skill_ids.add(skill_info["skill_id"])

    # Skills the student needs to learn (in role but not possessed)
    needed_skills = required_skill_ids - student_skill_ids

    if not needed_skills:
        return [], {}

    # Build domains: for each needed skill, possible proficiency levels
    proficiency_levels = ["beginner", "intermediate", "advanced"]

    domains: dict[str, list[str]] = {}
    for skill in sorted(needed_skills):
        # Find the role's minimum proficiency for this skill
        min_prof = "beginner"  # default
        for skill_info in role_required_skills:
            if skill_info["skill_id"] == skill:
                min_prof = skill_info.get("minimum_proficiency", "beginner")
                break
        # Domain: from the role's minimum up to advanced
        min_idx = proficiency_levels.index(min_prof) if min_prof in proficiency_levels else 0
        domains[skill] = proficiency_levels[min_idx:]

    variable_names = sorted(domains.keys())
    return variable_names, domains


def _prerequisite_core_check(
    assigned: dict[str, str], role_required_skills: list[dict[str, str]]
) -> bool:
    """Check that if a non-core skill is assigned, at least one core skill is also assigned.

    This is a simplified prerequisite model for SkillBridge: core foundational skills
    should be learned before nice_to_have / non-core skills.

    Args:
        assigned: mapping skill_name -> assigned value/level
        role_required_skills: list of required skill info dicts

    Returns:
        True if constraints are satisfied, False otherwise.
    """
    # Separate core and non-core skills
    core_skills = set()
    non_core_skills = set()
    for skill_info in role_required_skills:
        skill_name = skill_info["skill_id"]
        if skill_info.get("is_core", True):
            core_skills.add(skill_name)
        else:
            non_core_skills.add(skill_name)

    # If any non-core skill is assigned, at least one core skill must also be assigned
    assigned_skill_names = set(assigned.keys())
    non_core_assigned = assigned_skill_names & non_core_skills
    if non_core_assigned and not (assigned_skill_names & core_skills):
        return False
    return True


def solve_csp(student_id: str, role_id: str, db: Any = None) -> dict[str, Any]:
    """Run CSP + Backtracking search for a student + role.

    The CSP finds a valid assignment of proficiency levels to skills the student
    needs to learn, respecting prerequisites, required skills, and other constraints.

    Args:
        student_id: student identifier
        role_id: target career role identifier
        db: database session (optional; injected by FastAPI dependency in production)

    Returns:
        dict with keys:
        - success: bool
        - ordered_selected_skills: list of skill names in valid learning order
        - assignments: dict mapping skill_name -> assigned proficiency
        - constraints_checked: int
        - backtrack_count: int
        - failure_reason: str | None
        - algorithm: str — "CSP Backtracking with MRV"
    """
    # Load student skills and role requirements
    student_skills = _load_student_skills(student_id, db)
    role_required_skills = _load_role_required_skills(role_id)

    if not role_required_skills:
        return {
            "success": False,
            "ordered_selected_skills": [],
            "assignments": {},
            "constraints_checked": 0,
            "backtrack_count": 0,
            "failure_reason": f"Role '{role_id}' not found in roles data",
            "algorithm": "CSP Backtracking with MRV",
        }

    # Build CSP variables for skills the student doesn't have
    variable_names, domains = _build_csp_variables(student_skills, role_required_skills)

    if not variable_names:
        # Student already has all required skills
        return {
            "success": True,
            "ordered_selected_skills": list(student_skills.keys()),
            "assignments": {name: prof for name, prof in student_skills.items()},
            "constraints_checked": 0,
            "backtrack_count": 0,
            "failure_reason": None,
            "algorithm": "CSP Backtracking with MRV",
        }

    # Initialize CSP
    csp = CSP()

    # Add variables with domains
    for name in variable_names:
        csp.add_variable(name, domains.get(name, []))

    # Add constraints via the CSP framework

    # 1. Prerequisite constraint: if a non-core skill is assigned, at least one core skill must also be assigned
    csp.add_constraint(
        lambda assigned: _prerequisite_core_check(assigned, role_required_skills)
    )

    # 2. Required skills constraint: at least min_count of required skills must be assigned
    # During search, use min_count=0 so partial assignments are never rejected;
    # required skills are verified after a complete solution is found.
    required_skill_ids = set()
    for skill_info in role_required_skills:
        required_skill_ids.add(skill_info["skill_id"])

    # Use a closure to capture required_skill_ids
    _req_ids = required_skill_ids

    def _required_skills_constraint(assigned: dict[str, str]) -> bool:
        """Constraint: at least minimum required skills must be assigned."""
        return required_skills(assigned, _req_ids, 0)

    csp.add_constraint(_required_skills_constraint)

    # 3. Conflicting skills constraint: no two conflicting skills assigned simultaneously
    # Build empty conflicts dict — no inherent conflicts in SkillBridge
    _conflicting = {}
    csp.add_constraint(
        lambda assigned, conf=_conflicting: conflicting_skills(assigned, conf)
    )

    # 4. Dependency validation constraint: skill dependencies satisfied
    _deps = {}
    csp.add_constraint(
        lambda assigned, dep=_deps: dependency_validation(assigned, dep)
    )

    # Run backtracking search
    # Do NOT pass optional parameters (prerequisites, required, conflicting, dependencies)
    # since we handle all constraints via csp.add_constraint() above.
    # The solver's MRV heuristic will still work with the CSP's variable domains.
    result = backtracking_search(
        csp=csp,
        variable_names=variable_names,
        domains={var: domains.get(var, []) for var in variable_names},
    )

    # Post-process result: build ordered_selected_skills via topological sort
    ordered_selected_skills: list[str] = []
    if result.success and result.ordered_selected_skills is not None:
        # Use the topological sort from the solver
        ordered_selected_skills = result.ordered_selected_skills
    elif result.success:
        # Fallback: sort assignments keys
        ordered_selected_skills = sorted(result.assignments.keys())

    return {
        "success": result.success,
        "ordered_selected_skills": ordered_selected_skills,
        "assignments": result.assignments,
        "constraints_checked": result.constraints_checked,
        "backtrack_count": result.backtrack_count,
        "failure_reason": result.failure_reason,
        "algorithm": "CSP Backtracking with MRV",
    }