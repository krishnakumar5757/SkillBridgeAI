"""Plain-Python constraint functions/classes for SkillBridge Module 4.

Constraints:
  - prerequisite ordering
  - required skills
  - conflicting skills
  - dependency validation
"""

from __future__ import annotations


def prerequisite_ordering(
    assigned: dict[str, str],
    prerequisites: dict[str, list[str]],
) -> bool:
    """Constraint: for each skill, its prerequisites must already be assigned.

    Args:
        assigned: mapping skill_name -> assigned value/level
        prerequisites: mapping skill_name -> list of prerequisite skill names

    Returns:
        True if all prerequisite dependencies are satisfied, False otherwise.
    """
    for skill, reqs in prerequisites.items():
        if skill in assigned:
            for prereq in reqs:
                if prereq not in assigned:
                    return False
    return True


def required_skills(
    assigned: dict[str, str],
    required: set[str],
    min_count: int = 1,
) -> bool:
    """Constraint: at least `min_count` of the required skills must be assigned.

    During a CSP search, use min_count=0 so partial assignments are never
    rejected for missing required skills. The final solution will be
    verified separately (see solver post-check).

    Args:
        assigned: mapping skill_name -> assigned value/level
        required: set of skill names that should be present
        min_count: minimum number of required skills that must be assigned

    Returns:
        True if the minimum count of required skills is satisfied.
        During search, pass min_count=0 to never reject partial assignments.
    """
    covered = [s for s in required if s in assigned]
    return len(covered) >= min_count


def conflicting_skills(
    assigned: dict[str, str],
    conflicting: dict[str, list[str]],
) -> bool:
    """Constraint: no two conflicting skills may be assigned simultaneously.

    Args:
        assigned: mapping skill_name -> assigned value/level
        conflicting: mapping skill_name -> list of skill names/values that conflict with it

    Returns:
        True if no conflicts exist, False otherwise.
    """
    for skill, conflicts in conflicting.items():
        if skill in assigned:
            skill_value = assigned[skill]
            for conflict in conflicts:
                # Check if any assigned skill has a value that conflicts
                for assigned_name, assigned_value in assigned.items():
                    if assigned_value == conflict:
                        return False
    return True


def dependency_validation(
    assigned: dict[str, str],
    dependencies: dict[str, list[str]],
) -> bool:
    """Constraint: validate that skill dependencies are satisfied.

    Args:
        assigned: mapping skill_name -> assigned value/level
        dependencies: mapping skill_name -> list of dependency skill names

    Returns:
        True if all dependencies are satisfied, False otherwise.
    """
    for skill, deps in dependencies.items():
        if skill in assigned:
            for dep in deps:
                if dep not in assigned:
                    return False
    return True