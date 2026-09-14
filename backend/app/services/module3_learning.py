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

from pathlib import Path
from typing import Any

from app.utils import normalize_role_required_skills


def _import_astar():
    """Import A* modules with path setup."""
    import importlib
    import sys

    astar_path = Path(__file__).resolve().parents[3] / "modules" / "module-3-learning-intelligence" / "astar"
    astar_path_str = str(astar_path)
    if astar_path_str not in sys.path:
        sys.path.insert(0, astar_path_str)

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
        best: dict[str, int] = {}

        prof_map = {"beginner": 1, "intermediate": 2, "advanced": 3}
        prof_names = {rank: name for name, rank in prof_map.items()}

        for ss, skill in student_skills:
            sid = skill.id
            prof_rank = prof_map.get(ss.proficiency, 1)

            if sid not in best or prof_rank > best[sid]:
                best[sid] = prof_rank
                skills[sid] = prof_names[prof_rank]

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


def _to_astar_vocabulary_keys(
    db,
    student_skills: dict[str, str],
    role_required_skills: list[dict[str, Any]],
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """Adapt database UUIDs to the canonical keys used by the A* vocabulary.

    UUIDs remain the database representation, while the A* vocabulary currently
    identifies skills by canonical names (or vocabulary IDs). This adapter keeps
    that translation at the integration boundary instead of changing A*.
    """
    from app.models.skill import Skill

    skill_ids = set(student_skills)
    skill_ids.update(
        requirement["skill_id"]
        for requirement in role_required_skills
        if requirement.get("skill_id") is not None
    )
    names_by_id = {
        skill_id: skill_name
        for skill_id, skill_name in db.query(Skill.id, Skill.name)
        .filter(Skill.id.in_(skill_ids))
        .all()
    }

    astar_student_skills = {
        names_by_id.get(skill_id, skill_id): proficiency
        for skill_id, proficiency in student_skills.items()
    }
    astar_role_skills = []
    for requirement in role_required_skills:
        adapted = dict(requirement)
        canonical_name = names_by_id.get(adapted.get("skill_id"), adapted.get("skill_name"))
        if canonical_name:
            adapted["skill_id"] = canonical_name
            adapted["skill_name"] = canonical_name
        astar_role_skills.append(adapted)

    return astar_student_skills, astar_role_skills


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

    # 3. Normalize role requirements once before passing them to the A* integration.
    student_skill_ids = set(student_skills.keys())
    normalized_role_skills = normalize_role_required_skills(db, role_required_skills)
    unresolved_role_skills = [
        requirement["skill_name"]
        for requirement in normalized_role_skills
        if requirement["skill_id"] is None
    ]
    if unresolved_role_skills:
        return {
            "roadmap": {
                "target_role": role_id,
                "learning_steps": [],
                "total_estimated_cost": 0.0,
                "skills_acquired": 0,
                "skills_remaining": len(unresolved_role_skills),
                "algorithm": "A* Search with f(n)=g(n)+h(n)",
                "unresolved_role_skills": unresolved_role_skills,
            },
            "total_estimated_cost": 0.0,
            "nodes_expanded": 0,
            "search_depth": 0,
            "goal_reached": False,
            "unresolved_role_skills": unresolved_role_skills,
        }

    # Adapt UUID-normalized database data to the canonical A* vocabulary keys.
    astar_student_skills, astar_role_skills = _to_astar_vocabulary_keys(
        db, student_skills, normalized_role_skills
    )
    skill_graph = BUILD_GRAPH_FROM_ROLES(
        astar_role_skills, set(astar_student_skills)
    )

    # 4. Run A* Search to find the minimum-cost learning path
    result = A_STAR_SEARCH(
        student_skills=astar_student_skills,
        target_role_id=role_id,
        role_required_skills=astar_role_skills,
        skill_graph=skill_graph,
    )

    # 5. Post-process: set the target_role in the roadmap
    if "roadmap" in result and result["roadmap"]:
        result["roadmap"]["target_role"] = role_id

    return result
