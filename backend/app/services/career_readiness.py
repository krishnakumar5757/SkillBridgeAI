"""Career Readiness Service for SkillBridge Module 4.

Evaluates a student's readiness for a target career role based on:
- Skill coverage (how many required skills the student has)
- Proficiency match (whether current proficiency meets role requirements)
- Skill gaps (missing and below-required skills)
- Core skill importance

Uses the project's existing Skill Gap analysis and utility constants.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.utils.constants import (
    PROFICIENCY_BEGINNER,
    PROFICIENCY_INTERMEDIATE,
    PROFICIENCY_ADVANCED,
    PROFICIENCY_LEVELS,
)
from app.services.module2_career import get_student_skills, analyze_skill_gap
from app.models.student import Student
from app.utils import normalize_role_required_skills

# Role data loaded from roles.json
_ROLES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "data",
    "roles",
    "roles.json",
)

try:
    with open(_ROLES_PATH, encoding="utf-8") as f:
        _ROLES_DATA = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    _ROLES_DATA = []

_ROLES_BY_ID = {}
for role in _ROLES_DATA:
    _ROLES_BY_ID[role["id"]] = role


def _load_role_required_skills(role_id: str) -> list[dict[str, str]]:
    """Load role's required skills from roles.json."""
    role = _ROLES_BY_ID.get(role_id)
    if role is not None:
        return role["required_skills"]
    return []


def _proficiency_rank(prof: str) -> int:
    """Convert proficiency string to numeric rank (beginner=1, intermediate=2, advanced=3)."""
    return PROFICIENCY_LEVELS.get(prof, 1)


def _compute_readiness_score(
    total_required: int,
    skills_met: list[dict[str, Any]],
    skills_missing: list[dict[str, Any]],
    skills_below: list[dict[str, Any]],
    core_skills_met: int,
    total_core: int,
) -> dict[str, Any]:
    """Compute the 0–100 readiness score and breakdown."""
    # --- 1. Coverage (40% weight) ---
    acquired_count = len(skills_met) + len(skills_below)
    coverage_fraction = acquired_count / total_required if total_required > 0 else 1.0
    coverage_percentage = coverage_fraction * 100

    # --- 2. Proficiency match (40% weight) ---
    proficient_count = 0
    total_profiled = 0
    for s in skills_met:
        current = s["current_proficiency"]  # numeric rank from get_student_skills
        required = PROFICIENCY_LEVELS.get(s["required_proficiency"], 1)  # convert string to numeric
        if current >= required:
            proficient_count += 1
        total_profiled += 1

    proficient_fraction = (proficient_count / total_profiled) if total_profiled > 0 else 1.0
    proficiency_percentage = proficient_fraction * 100

    # --- 3. Core skill coverage (15% weight) ---
    core_fraction = (core_skills_met / total_core) if total_core > 0 else 1.0
    core_percentage = core_fraction * 100

    # --- 4. Gap penalty (5% weight) ---
    missing_count = len(skills_missing)
    below_count = len(skills_below)
    gap_penalty = (missing_count * 3 + below_count * 1) * (5.0 / total_required) if total_required > 0 else 0.0
    gap_penalty = min(gap_penalty, 5.0)

    # --- Final score --- weighted sum with actual weights
    weighted_score = (coverage_percentage * 0.40
                    + proficiency_percentage * 0.40
                    + core_percentage * 0.15
                    - gap_penalty)
    final_score = max(0.0, min(100.0, round(weighted_score)))

    # --- Readiness level ---
    if final_score >= 80:
        level = "Ready"
    elif final_score >= 60:
        level = "Nearly Ready"
    elif final_score >= 40:
        level = "Developing"
    else:
        level = "Not Ready"

    return {
        "raw_score": weighted_score,
        "final_score": final_score,
        "level": level,
        "coverage_fraction": coverage_fraction,
        "proficient_fraction": proficient_fraction,
        "core_fraction": core_fraction,
        "gap_penalty": gap_penalty,
        "acquired_count": acquired_count,
        "total_required": total_required,
        "proficient_count": proficient_count,
        "total_profiled": total_profiled,
        "core_skills_met": core_skills_met,
        "total_core": total_core,
        "missing_count": missing_count,
        "below_count": below_count,
        "coverage_percentage": round(coverage_percentage, 1),
        "proficiency_percentage": round(proficiency_percentage, 1),
    }


def analyze_career_readiness(student_id: str, role_id: str, db: Session = None) -> dict[str, Any]:
    """Analyze a student's career readiness for a target role."""
    # Use provided session or create a new one
    if db is None:
        db = SessionLocal()

    try:
        # --- Check if student exists in the database ---
        from app.models.student import Student as StudentModel

        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if student is None:
            return {
                "readiness_score": 0,
                "readiness_level": "Not Ready",
                "total_required_skills": 0,
                "skills_met": [],
                "skills_missing": [],
                "skills_below": [],
                "coverage_percentage": 0.0,
                "proficiency_percentage": 0.0,
                "strengths": [],
                "priority_gaps": [],
                "recommendations": [f"Student '{student_id}' not found in the database."],
                "roadmap_summary": "",
                "summary": f"Student '{student_id}' could not be found. Cannot assess career readiness.",
                "algorithm": "Career Readiness Analysis",
            }

        # --- Load role requirements ---
        role_required_skills = _load_role_required_skills(role_id)
        if not role_required_skills:
            return {
                "readiness_score": 0,
                "readiness_level": "Not Ready",
                "total_required_skills": 0,
                "skills_met": [],
                "skills_missing": [],
                "skills_below": [],
                "coverage_percentage": 0.0,
                "proficiency_percentage": 0.0,
                "strengths": [],
                "priority_gaps": [],
                "recommendations": [f"Role '{role_id}' not found in role definitions."],
                "roadmap_summary": "",
                "summary": f"Role '{role_id}' could not be found. Cannot assess career readiness.",
                "algorithm": "Career Readiness Analysis",
            }

        normalized_role_required_skills = normalize_role_required_skills(db, role_required_skills)

        # --- Get student skills from DB using existing helper ---
        student_skills = get_student_skills(db, student_id)

        # Build a name-indexed lookup since role required skills use skill names
        # as skill_id, but get_student_skills keys are DB skill UUIDs.
        student_skills_by_name: dict[str, dict[str, Any]] = {}
        for skill_id, skill_info in student_skills.items():
            student_skills_by_name[skill_info["skill_name"]] = {
                **skill_info,
                "skill_id": skill_id,
            }

        # --- Build gap analysis structure ---
        skills_met: list[dict[str, Any]] = []
        skills_missing: list[dict[str, Any]] = []
        skills_below: list[dict[str, Any]] = []

        # Get role required skill IDs
        required_skill_ids = set()
        for skill_info in normalized_role_required_skills:
            required_skill_ids.add(skill_info["skill_id"])

        # Analyze each required skill
        for req_skill in normalized_role_required_skills:
            skill_name = req_skill.get("skill_name") or req_skill.get("skill_id") or "Unknown skill"
            skill_id = req_skill.get("skill_id") or skill_name
            required_prof = req_skill.get("minimum_proficiency", "intermediate")
            priority = req_skill.get("priority", "important")
            is_core = req_skill.get("is_core", False)

            if skill_name in student_skills_by_name:
                # Student has this skill - check proficiency
                student_prof = student_skills_by_name[skill_name]["proficiency"]
                # get_student_skills already returns numeric rank (1=beginner, 2=intermediate, 3=advanced)
                # Convert required_prof string to numeric for comparison
                from app.utils.constants import PROFICIENCY_LEVELS
                required_rank = PROFICIENCY_LEVELS.get(required_prof, PROFICIENCY_BEGINNER)

                # Determine match status using numeric ranks
                if student_prof >= required_rank:
                    match_status = "Strong"
                elif student_prof >= required_rank - 1:
                    match_status = "Weak"
                else:
                    match_status = "Missing"

                result = {
                    "skill_id": student_skills_by_name[skill_name]["skill_id"],
                    "skill_name": student_skills_by_name[skill_name]["skill_name"],
                    "required_proficiency": required_prof,
                    "current_proficiency": student_prof,
                    "match_status": match_status,
                    "gap_score": 0,
                    "priority": priority,
                    "is_core": is_core,
                }

                if match_status == "Strong":
                    skills_met.append(result)
                elif match_status == "Weak":
                    skills_below.append(result)
                else:
                    skills_missing.append(result)

            else:
                # Student does not have this skill at all - it's missing
                skills_missing.append({
                    "skill_id": skill_id,
                    "skill_name": skill_name,
                    "required_proficiency": required_prof,
                    "current_proficiency": None,
                    "match_status": "Missing",
                    "gap_score": 3,
                    "priority": priority,
                    "is_core": is_core,
                })

        # --- Core skill counting ---
        total_core = sum(1 for s in role_required_skills if s.get("is_core", False))
        core_skills_met = sum(
            1 for s in skills_met if s.get("is_core", False)
        )

        # --- Compute readiness score ---
        total_required = len(role_required_skills)
        score_breakdown = _compute_readiness_score(
            total_required=total_required,
            skills_met=skills_met,
            skills_missing=skills_missing,
            skills_below=skills_below,
            core_skills_met=core_skills_met,
            total_core=total_core,
        )

        # --- Strengths ---
        strengths: list[str] = []
        for s in skills_met:
            if s.get("match_status") == "Strong":
                strengths.append("%s: %s meets %s requirement" % (s['skill_name'], s['current_proficiency'], s['required_proficiency']))
            elif s.get("match_status") == "Weak":
                strengths.append("%s: near-match at %s" % (s['skill_name'], s['current_proficiency']))

        # --- Priority gaps ---
        priority_gaps: list[str] = []
        for s in skills_missing:
            priority = s.get("priority", "important")
            priority_gaps.append("Missing critical skill: %s (%s required)" % (s['skill_name'], s['required_proficiency']))
        for s in skills_below:
            priority = s.get("priority", "important")
            priority_gaps.append("Below required: %s (have %s, need %s)" % (s['skill_name'], s['current_proficiency'], s['required_proficiency']))

        # --- Recommendations ---
        recommendations: list[str] = []
        if skills_missing:
            rec_skills = ", ".join(s["skill_name"] for s in skills_missing[:3])
            recommendations.append("Focus on acquiring %s skill(s): %s" % (len(skills_missing), rec_skills))
        if skills_below:
            rec_skills = ", ".join(s["skill_name"] for s in skills_below[:3])
            recommendations.append("Bridge %s below-required skill(s): %s" % (len(skills_below), rec_skills))
        coverage_pct = score_breakdown["coverage_fraction"] * 100
        if coverage_pct < 50:
            recommendations.append("Consider foundational skill development before role-specific learning.")
        elif coverage_pct < 80:
            recommendations.append("Prioritize closing the most critical skill gaps before role assessment.")

        # --- Roadmap summary (CSP context) ---
        roadmap_summary = ""
        try:
            from app.services.csp_service import solve_csp
            csp_result = solve_csp(student_id, role_id, db=db)
            if csp_result.get("success"):
                ordered = csp_result.get("ordered_selected_skills", [])
                if ordered:
                    roadmap_summary = "CSP-determined learning path: %s and %d more skills." % (", ".join(ordered[:3]), len(ordered) - 3)
        except Exception:
            roadmap_summary = ""

        # --- Human-readable summary ---
        score = score_breakdown["final_score"]
        level = score_breakdown["level"]
        cov_pct = score_breakdown["coverage_fraction"] * 100
        prof_pct = score_breakdown["proficient_fraction"] * 100

        summary_parts = []
        summary_parts.append("Readiness score: %d/100 (%s)" % (score, level))
        summary_parts.append("Skill coverage: %.0f%% of %d required skills" % (cov_pct, total_required))
        summary_parts.append("Proficiency match: %.0f%% of skills at or above required level" % prof_pct)

        if skills_missing:
            summary_parts.append("Missing %d skill(s): %s" % (len(skills_missing), ", ".join(s["skill_name"] for s in skills_missing[:3])))
        if skills_below:
            summary_parts.append("Below required proficiency: %d skill(s): %s" % (len(skills_below), ", ".join(s["skill_name"] for s in skills_below[:3])))

        if strengths:
            summary_parts.append("Strengths: %s" % "; ".join(strengths[:3]))

        summary_parts.append(roadmap_summary if roadmap_summary else "Review skill gaps and prioritize learning.")

        summary = " | ".join(summary_parts)

        return {
            "readiness_score": score_breakdown["final_score"],
            "readiness_level": score_breakdown["level"],
            "total_required_skills": total_required,
            "skills_met": skills_met,
            "skills_missing": skills_missing,
            "skills_below": skills_below,
            "coverage_percentage": round(score_breakdown["coverage_fraction"] * 100, 1),
            "proficiency_percentage": round(score_breakdown["proficient_fraction"] * 100, 1),
            "strengths": strengths,
            "priority_gaps": priority_gaps,
            "recommendations": recommendations,
            "roadmap_summary": roadmap_summary,
            "summary": summary,
            "algorithm": "Career Readiness Analysis",
        }
    finally:
        # Close the session if we created one (not if provided by caller)
        try:
            if db is not None:
                db.close()
        except Exception:
            pass
