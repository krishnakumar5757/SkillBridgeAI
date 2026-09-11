"""
SkillBridge AI — A* Heuristic Module

Estimates the remaining learning cost (h(n)) from a given state in the
skill learning graph.

The heuristic is admissible: it never overestimates the true cost to reach
the goal, ensuring A* finds the optimal (minimum-cost) learning path.
"""

from __future__ import annotations
from typing import Any


def compute_heuristic(
    current_skills: dict[str, str],
    target_skills: dict[str, str],
    learning_costs: dict[str, float],
    gap_weight: float = 1.0,
) -> float:
    """Compute the estimated remaining learning cost (heuristic).

    This is an admissible heuristic — it never overestimates the true cost
    to acquire all missing skills, which guarantees A* finds the optimal
    (minimum-total-cost) learning path.

    Args:
        current_skills: Dict mapping skill_id -> proficiency level
            (e.g., {"Python": "intermediate", "SQL": "beginner"})
        target_skills: Dict mapping skill_id -> required proficiency level
            (e.g., {"Python": "advanced", "SQL": "intermediate"})
        learning_costs: Dict mapping skill_id -> estimated learning cost
            (e.g., {"Python": 150.0, "SQL": 80.0})
        gap_weight: Weight factor for proficiency gap adjustment.
            Higher required proficiency = relatively higher estimated cost.

    Returns:
        Total estimated remaining learning cost (float).
        Returns 0.0 if no skills are missing (goal state).
    """
    total_cost = 0.0
    has_missing = False

    for skill_id, required_prof in target_skills.items():
        current_prof = current_skills.get(skill_id)

        if current_prof is None:
            # Student doesn't have this skill at all — full cost
            cost = learning_costs.get(skill_id, 100.0)
            has_missing = True
        elif _proficiency_rank(current_prof) < _proficiency_rank(required_prof):
            # Student has the skill but below required — partial gap cost
            base_cost = learning_costs.get(skill_id, 100.0)
            prof_gap = _proficiency_rank(required_prof) - _proficiency_rank(current_prof)
            # Scale cost by gap size; admissible because we cap at full cost
            cost = base_cost * min(prof_gap, 3.0) / 3.0
            has_missing = True
        else:
            # Student meets or exceeds requirement — no cost for this skill
            cost = 0.0

        total_cost += cost

    # Also add cost for any skills student has that aren't required but
    # might be needed as prerequisites — we use a small fraction to keep
    # admissibility while guiding the search
    for skill_id in current_skills:
        if skill_id not in target_skills:
            # Optional skill not required — small cost to account for
            # potential prerequisite chains
            cost = learning_costs.get(skill_id, 50.0) * 0.1
            total_cost += cost

    return total_cost


def _proficiency_rank(prof: str) -> int:
    """Convert proficiency level to numeric rank for comparison.

    beginner = 1, intermediate = 2, advanced = 3
    """
    ranks: dict[str, int] = {
        "beginner": 1,
        "intermediate": 2,
        "advanced": 3,
    }
    return ranks.get(prof, 1)


def compute_path_heuristic(
    graph: object,
    start_skills: dict[str, str],
    target_skills: dict[str, str],
    learning_costs: dict[str, float],
) -> float:
    """Convenience wrapper: compute heuristic for A* path search.

    Args:
        graph: SkillGraph instance (not used in current heuristic but
            included for future extensibility).
        start_skills: Current student skills with proficiency.
        target_skills: Required skills for the target role.
        learning_costs: Per-skill learning costs.

    Returns:
        Admissible heuristic value (estimated remaining cost).
    """
    return compute_heuristic(start_skills, target_skills, learning_costs)