"""
SkillBridge AI — Career Intelligence Service

Compares a student's current skills against a selected career role's
requirements and produces a skill gap report.
"""

from __future__ import annotations

from typing import Any

from app.utils.constants import (
    MATCH_STRONG,
    MATCH_WEAK,
    MATCH_MISSING,
    PROFICIENCY_BEGINNER,
    PROFICIENCY_INTERMEDIATE,
    PROFICIENCY_ADVANCED,
    PROFICIENCY_LEVELS,
)
from app.utils import normalize_role_required_skills
from app.models.skill import Skill, StudentSkill
from app.models.student import Student


# Proficiency level mapping: beginner=1, intermediate=2, advanced=3
PROFICIENCY_SCALE: dict[str, int] = {
    "beginner": PROFICIENCY_BEGINNER,
    "intermediate": PROFICIENCY_INTERMEDIATE,
    "advanced": PROFICIENCY_ADVANCED,
}

def get_student_skills(db, student_id: str) -> dict[str, dict[str, Any]]:
    """Get all skills for a student, returning {skill_id: {proficiency, source, confidence}}.

    Returns a dictionary mapping skill_id to the highest-proficiency version
    of that skill across all sources (resume takes precedence over self-reported).
    """
    student_skills = (
        db.query(StudentSkill, Skill)
        .filter(StudentSkill.student_id == student_id)
        .filter(StudentSkill.skill_id == Skill.id)
        .all()
    )

    # Build map: skill_id -> best proficiency across sources
    # Priority: resume > self-reported (resume evidence upgrades proficiency)
    best: dict[str, dict[str, Any]] = {}

    for ss, skill in student_skills:
        sid = skill.id
        prof = PROFICIENCY_SCALE.get(ss.proficiency, PROFICIENCY_BEGINNER)

        if sid not in best:
            best[sid] = {
                "proficiency": prof,
                "source": ss.source,
                "confidence": ss.confidence,
                "skill_name": skill.name,
                "category": skill.category,
            }
        else:
            # Resume skills upgrade self-reported proficiency
            if ss.source == "resume" and prof > best[sid]["proficiency"]:
                best[sid] = {
                    "proficiency": prof,
                    "source": ss.source,
                    "confidence": ss.confidence,
                    "skill_name": skill.name,
                    "category": skill.category,
                }
            # If same source, keep higher proficiency
            elif prof > best[sid]["proficiency"]:
                best[sid] = {
                    "proficiency": prof,
                    "source": ss.source,
                    "confidence": ss.confidence,
                    "skill_name": skill.name,
                    "category": skill.category,
                }

    return best


def get_role_skills(role_id: str) -> list[dict[str, Any]] | None:
    """Load required skills for a career role from the roles data.

    Returns the role's required skills list, or None if role not found.
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


def compute_gap(
    required_prof: int,
    current_prof: int,
) -> tuple[str, int]:
    """Compute match status and gap score.

    Returns (match_status, gap_score) where:
    - gap_score = required_proficiency - current_proficiency
    - MATCH_STRONG if gap_score <= 0 (student meets/exceeds requirement)
    - MATCH_WEAK if gap_score == 1 (student one level below)
    - MATCH_MISSING if gap_score >= 2 (student two+ levels below, or skill missing)
    """
    gap_score = required_prof - current_prof

    if gap_score <= 0:
        return MATCH_STRONG, max(0, gap_score)
    elif gap_score == 1:
        return MATCH_WEAK, gap_score
    else:
        # gap_score >= 2: skill is missing or very weak
        return MATCH_MISSING, gap_score


def analyze_skill_gap(
    db,
    student_id: str,
    role_id: str,
) -> dict[str, Any]:
    """Analyze skill gaps for a student against a career role.

    Returns a comprehensive gap analysis including:
    - matched skills (strong)
    - weak skills (one level below)
    - missing skills (two+ levels below or not have the skill)
    - overall gap metrics
    """
    if db.query(Student).filter(Student.id == student_id).first() is None:
        raise ValueError(f"Student with id {student_id} not found")

    # Get student's current skills
    student_skills = get_student_skills(db, student_id)

    # Get role's required skills
    role_required = get_role_skills(role_id)
    if role_required is None:
        raise ValueError(f"Role with id {role_id} not found")
    normalized_role_required = normalize_role_required_skills(db, role_required)

    # Build set of student skill IDs
    student_skill_ids = set(student_skills.keys())

    # Analyze each required skill
    matched_strong: list[dict[str, Any]] = []
    matched_weak: list[dict[str, Any]] = []
    matched_missing: list[dict[str, Any]] = []

    total_required = len(role_required)
    total_acquired = 0

    for req_skill in normalized_role_required:
        skill_uuid = req_skill["skill_id"]
        skill_name = req_skill.get("skill_name") or "Unknown skill"
        required_prof = PROFICIENCY_SCALE.get(
            req_skill["minimum_proficiency"], PROFICIENCY_INTERMEDIATE
        )
        priority = req_skill.get("priority", "important")
        is_core = req_skill.get("is_core", False)

        if skill_uuid is not None and skill_uuid in student_skill_ids:
            # Student has this skill - check proficiency
            current_prof = student_skills[skill_uuid]["proficiency"]
            gap_status, gap_score = compute_gap(required_prof, current_prof)

            result = {
                "skill_id": skill_name,
                "skill_name": skill_name,
                "required_proficiency": req_skill["minimum_proficiency"],
                "current_proficiency": list(PROFICIENCY_LEVELS.keys())[
                    list(PROFICIENCY_LEVELS.values()).index(current_prof)
                ]
                if current_prof in PROFICIENCY_LEVELS.values()
                else "beginner",
                "match_status": gap_status,
                "gap_score": gap_score,
                "priority": priority,
                "is_core": is_core,
            }

            if gap_status == MATCH_STRONG:
                matched_strong.append(result)
                total_acquired += 1
            elif gap_status == MATCH_WEAK:
                matched_weak.append(result)
            else:
                matched_missing.append(result)
        else:
            # Student does not have this skill at all - it's missing
            result = {
                "skill_id": skill_name,
                "skill_name": skill_name,
                "required_proficiency": req_skill["minimum_proficiency"],
                "current_proficiency": None,
                "match_status": MATCH_MISSING,
                "gap_score": 3,  # Missing = 3 levels gap
                "priority": priority,
                "is_core": is_core,
            }
            matched_missing.append(result)

    # Compute coverage metrics
    total_skills_required = total_required
    skill_coverage_percent = (total_acquired / total_skills_required * 100) if total_skills_required > 0 else 0.0

    # Core skills only
    core_required = [s for s in normalized_role_required if s.get("is_core", False)]
    core_acquired = sum(
        1 for s in core_required
        if s["skill_id"] is not None
        and s["skill_id"] in student_skill_ids
        and student_skills[s["skill_id"]]["proficiency"]
        >= PROFICIENCY_SCALE.get(s["minimum_proficiency"], PROFICIENCY_INTERMEDIATE)
    )
    core_skill_coverage_percent = (core_acquired / len(core_required) * 100) if core_required else 0.0

    # Critical priority skills only
    critical_required = [s for s in normalized_role_required if s.get("priority") == "critical"]
    critical_acquired = sum(
        1 for s in critical_required
        if s["skill_id"] is not None
        and s["skill_id"] in student_skill_ids
        and student_skills[s["skill_id"]]["proficiency"]
        >= PROFICIENCY_SCALE.get(s["minimum_proficiency"], PROFICIENCY_INTERMEDIATE)
    )
    critical_skill_coverage_percent = (
        (critical_acquired / len(critical_required) * 100) if critical_required else 0.0
    )

    # Prioritize gaps: missing prerequisites first, then critical, then large gaps, then important, then small gaps, then nice-to-have
    # Sort missing skills: critical > important > nice_to_have, then by gap_score desc
    def missing_priority(skill: dict[str, Any]) -> tuple[int, int]:
        """Return (category_priority, gap_score) for sorting missing skills.

        Lower value = higher priority.
        """
        priority_order = {"critical": 0, "important": 1, "nice_to_have": 2}
        cat_priority = priority_order.get(skill.get("priority", "important"), 1)
        return (cat_priority, -skill["gap_score"])

    prioritized_missing = sorted(matched_missing, key=missing_priority)
    prioritized_weak = sorted(matched_weak, key=lambda s: (-PROFICIENCY_SCALE.get(s.get("current_proficiency", 1), 1), missing_priority(s)[1]))

    report = {
        "student_id": student_id,
        "role_id": role_id,
        "role_name": role_required[0].get("role_name", role_id) if role_required else "Unknown",
        "total_required_skills": total_skills_required,
        "matched_strong": matched_strong,
        "matched_weak": matched_weak,
        "matched_missing": matched_missing,
        "prioritized_missing": prioritized_missing,
        "prioritized_weak": prioritized_weak,
        # Coverage metrics
        "skill_coverage_percent": round(skill_coverage_percent, 1),
        "core_skill_coverage_percent": round(core_skill_coverage_percent, 1),
        "critical_skill_coverage_percent": round(critical_skill_coverage_percent, 1),
        "total_skills_acquired": total_acquired,
        "total_skills_required": total_skills_required,
        # Summary
        "summary": {
            "strong_count": len(matched_strong),
            "weak_count": len(matched_weak),
            "missing_count": len(matched_missing),
            "total_gaps": len(matched_weak) + len(matched_missing),
        },
    }

    return report


def generate_skill_gap_report(
    db,
    student_id: str,
    role_id: str,
) -> dict[str, Any]:
    """Generate a skill gap report for a student against a career role.

    Convenience wrapper that returns the full analysis report.
    """
    return analyze_skill_gap(db, student_id, role_id)
