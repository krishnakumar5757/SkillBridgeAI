"""
SkillBridge AI — Module 3 Learning Service

Provides A* Learning Roadmap generation by combining student skill data
from Module 1/2 with the A* search algorithm from Module 3.

The service orchestrates:
1. Loading student's current skills
2. Loading the selected role's required skills
3. Building the skill graph
4. Running A* search
5. Returning the personalized learning roadmap
"""

from typing import Any


def _import_astar():
    """Import A* modules with path setup."""
    import importlib
    import sys

    astar_path = r"D:\FOAI\Skillbridge\modules\module-3-learning-intelligence\astar"
    if astar_path not in sys.path:
        sys.path.insert(0, astar_path)

    # Import the algorithm and graph modules
    algorithm_mod = importlib.import_module("algorithm")
    graph_mod = importlib.import_module("graph")

    return algorithm_mod.a_star_search, graph_mod.build_graph_from_roles


A_STAR_SEARCH, BUILD_GRAPH_FROM_ROLES = _import_astar()


def get_student_skills_from_db(student_id: str, db) -> dict[str, str]:
    """Get student's current skills as {skill_id: proficiency}.

    Tries to get skills from the database first. Falls back to returning
    an empty dict if no skills are found (the A* algorithm will handle
    this case gracefully — all target skills will appear as missing).

    Args:
        student_id: The student's unique identifier.
        db: Database session.

    Returns:
        Dict mapping skill_id -> proficiency level string
        (e.g., {"Python": "intermediate", "SQL": "beginner"}).
    """
    try:
        from app.models.student import Student
        from app.models.skill import StudentSkill, Skill

        student_skills = (
            db.query(StudentSkill, Skill)
            .filter(StudentSkill.student_id == student_id)
            .filter(StudentSkill.skill_id == Skill.id)
            .all()
        )

        # Build map: skill_id -> best proficiency
        # Priority: resume > self-reported (resume evidence upgrades proficiency)
        skills: dict[str, str] = {}
        best: dict[int, str] = {}  # index -> proficiency string

        prof_map = {"beginner": "beginner", "intermediate": "intermediate", "advanced": "advanced"}

        for ss, skill in student_skills:
            sid = skill.id
            prof = prof_map.get(ss.proficiency, "beginner")

            if sid not in best or prof_map[prof] > best[sid]:
                best[sid] = prof
                skills[sid] = prof

        return skills

    except Exception:
        # If anything goes wrong with the database, return empty dict.
        # The A* algorithm handles the empty case — all target skills
        # will appear as missing and a roadmap will be generated.
        return {}


def get_role_required_skills(role_id: str) -> list[dict[str, Any]] | None:
    """Load required skills for a career role from the roles data.

    Args:
        role_id: The role identifier (software_engineer, data_analyst, frontend_developer).

    Returns:
        List of role skill dicts with skill_id, minimum_proficiency, priority, is_core,
        or None if role not found.
    """
    import json
    from pathlib import Path

    roles_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "roles" / "roles.json"
    if not roles_path.exists():
        return None

    with open(roles_path, encoding="utf-8") as f:
        roles = json.load(f)

    for role in roles:
        if role["id"] == role_id:
            return role["required_skills"]

    return None


def generate_learning_roadmap(
    student_id: str,
    role_id: str,
    db,
) -> dict[str, Any]:
    """Generate a personalized learning roadmap using A* Search.

    The flow:
    1. Load student's current skills from the database
    2. Load the selected role's required skills from roles data
    3. Build the skill learning graph from role requirements and student data
    4. Run A* Search to find the minimum-cost learning path
    5. Return the structured roadmap

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
        HTTPException: If student or role is not found.
    """
    # 1. Load student's current skills
    student_skills = get_student_skills_from_db(student_id, db)

    # 2. Load the selected role's required skills
    role_required_skills = get_role_required_skills(role_id)
    if role_required_skills is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail=f"Role with id {role_id} not found",
        )

    # 3. Build the skill learning graph from role requirements and student data
    student_skill_ids = set(student_skills.keys())
    skill_graph = BUILD_GRAPH_FROM_ROLES(role_required_skills, student_skill_ids)

    # 4. Run A* Search to find the minimum-cost learning path
    result = A_STAR_SEARCH(
        student_skills=student_skills,
        target_role_id=role_id,
        role_required_skills=role_required_skills,
        skill_graph=skill_graph,
    )

    # 5. Post-process: set the target_role in the roadmap
    if "roadmap" in result and result["roadmap"]:
        result["roadmap"]["target_role"] = role_id

    return result