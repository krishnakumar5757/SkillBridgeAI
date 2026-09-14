"""SkillBridge AI — Shared Utilities.

Shared utility functions used across modules.
"""

from __future__ import annotations

from typing import Any


def get_skill_id_by_name(db: Any, name: str | None) -> str | None:
    """Look up a skill's database UUID by its canonical name."""
    if db is None or not callable(getattr(db, "query", None)) or not name:
        return None

    from app.models.skill import Skill

    result = db.query(Skill.id).filter(Skill.name == name).first()
    if result is None:
        return None
    return result[0]


def normalize_role_required_skills(
    db: Any,
    role_required_skills: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Resolve role skill names to database UUIDs at the integration boundary.

    Unresolvable requirements retain their display name in ``skill_name`` and
    have ``skill_id`` set to ``None``. This lets each integration handle an
    unresolved requirement explicitly without mixing names into UUID sets.
    """
    normalized: list[dict[str, Any]] = []
    can_query = db is not None and callable(getattr(db, "query", None))
    for requirement in role_required_skills:
        role_skill_name = requirement.get("skill_name") or requirement.get("skill_id")
        display_name = (
            role_skill_name
            if isinstance(role_skill_name, str) and role_skill_name.strip()
            else "Unknown skill"
        )
        normalized_requirement = dict(requirement)
        normalized_requirement["skill_name"] = display_name
        normalized_requirement["skill_id"] = (
            get_skill_id_by_name(
                db,
                role_skill_name if isinstance(role_skill_name, str) else None,
            )
            if can_query
            else None
        )
        normalized.append(normalized_requirement)

    return normalized
