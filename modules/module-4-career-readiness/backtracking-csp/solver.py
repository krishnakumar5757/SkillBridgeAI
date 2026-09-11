"""Genuine recursive Backtracking Search with MRV for SkillBridge Module 4.

Implements:
  - choose an unassigned variable
  - use MRV (Minimum Remaining Values) when selecting the variable
  - try domain values deterministically
  - check constraints after each assignment
  - recurse
  - backtrack when a constraint fails
  - finish when every variable is assigned

The solver does NOT simply sort skills; it performs genuine CSP search
and produces a prerequisite-respecting ordered result.
"""

from __future__ import annotations

from typing import Any


class BacktrackResult:
    """Result returned by the backtracking solver."""

    def __init__(self):
        self.success = False
        self.ordered_selected_skills: list[str] = []
        self.assignments: dict[str, str] = {}
        self.constraints_checked = 0
        self.backtrack_count = 0
        self.failure_reason: str | None = None


def backtracking_search(
    csp: Any,
    variable_names: list[str] | None = None,
    domains: dict[str, list[str]] | None = None,
    prerequisites: dict[str, list[str]] | None = None,
    required: set[str] | None = None,
    conflicting: dict[str, list[str]] | None = None,
    dependencies: dict[str, list[str]] | None = None,
) -> BacktrackResult:
    """Recursive Backtracking Search with MRV for CSP.

    Args:
        csp: CSP instance with variables, domains, and constraints already set up.
        variable_names: optional list of variable names to use (for API-style calling).
        domains: mapping variable_name -> list of possible values.
        prerequisites: mapping skill_name -> list of prerequisite skill names.
        required: set of required skill names.
        conflicting: mapping skill_name -> list of conflicting skill names.
        dependencies: mapping skill_name -> list of dependency skill names.

    Returns:
        BacktrackResult with success, assignments, constraints_checked, backtrack_count,
        and failure_reason when unsuccessful.
    """
    result = BacktrackResult()

    # --- Initialise CSP if not already configured ---
    if csp is None:
        csp = CSP()

    # If we have variable names and domains, initialise the CSP
    if variable_names is not None and domains is not None:
        for name in variable_names:
            csp.add_variable(name, list(domains.get(name, [])))
        # Add constraints if provided
        if prerequisites is not None:
            csp.add_constraint(
                lambda assigned, pre=prerequisites: prerequisite_ordering(
                    assigned, pre
                )
            )
        if required is not None:
            # Use min_count=0 so partial assignments are never rejected;
            # required skills are verified after a complete solution is found.
            csp.add_constraint(
                lambda assigned, req=required, min=0: required_skills(
                    assigned, req, min
                )
            )
        if conflicting is not None:
            csp.add_constraint(
                lambda assigned, conf=conflicting: conflicting_skills(
                    assigned, conf
                )
            )
        if dependencies is not None:
            csp.add_constraint(
                lambda assigned, dep=dependencies: dependency_validation(
                    assigned, dep
                )
            )

# --- MRV helper: pick unassigned variable with smallest domain ---
    def mrv_variable(unassigned: list[Variable]) -> Variable | None:
        """Select the variable with the Minimum Remaining Values.

        Deterministic tie-breaking:
        1. Smaller domain size (primary MRV heuristic)
        2. Fewer unmet prerequisites (prefer variables whose prereqs can be satisfied first)
        3. Smaller variable name (deterministic tie-breaker)
        """
        if not unassigned:
            return None

        # Find minimum domain size
        min_domain = min(len(v.domain) for v in unassigned)
        # Filter to candidates with minimum domain
        candidates = [v for v in unassigned if len(v.domain) == min_domain]

        # Count unmet prerequisites for each candidate.
        # A prerequisite is "unmet" if it is still unassigned (present in the unassigned set).
        unassigned_names = {v.name for v in unassigned}

        def unmet_prereq_count(var: Variable) -> int:
            if prerequisites is None:
                return 0
            deps = prerequisites.get(var.name, [])
            return sum(1 for dep in deps if dep in unassigned_names)

        # Sort candidates: (unmet prerequisites, name) for determinism
        chosen = min(candidates, key=lambda v: (unmet_prereq_count(v), v.name))
        return chosen

    # --- Topological sort: order skills respecting prerequisites ---
    def topological_sort(assigned_skills: set[str], prereqs: dict[str, list[str]]) -> list[str]:
        """Produce a valid learning order for assigned skills.

        Uses Kahn-like algorithm: repeatedly pick the ready skill with
        the smallest name (deterministic). A skill is "ready" when all
        its prerequisites (that are also assigned) have already been placed.

        Returns list of skill names in valid order, or empty list if
        cannot resolve (should not happen with valid assignments).
        """
        skills = set(assigned_skills)
        ordered: list[str] = []
        remaining: set[str] = set(skills)

        while remaining:
            # Find skills whose assigned prerequisites are all already ordered
            ready: list[str] = []
            for skill in remaining:
                for prereq in prereqs.get(skill, []):
                    if prereq in skills and prereq in remaining:
                        break  # has an unmet prerequisite among assigned skills
                else:
                    # The loop completed without break → all prereqs satisfied
                    ready.append(skill)

            if not ready:
                # Cycle or unresolvable — return what we have
                break

            # Pick the smallest name for determinism
            chosen = min(ready)
            ordered.append(chosen)
            remaining.remove(chosen)

        return ordered

    # --- Recursive backtracking ---
    def recurse() -> bool:
        # All variables assigned?
        unassigned = [
            v for v in csp.variables if not csp.is_assigned(v)
        ]
        if not unassigned:
            # All assigned successfully — capture result before post-check
            result.assignments = {
                var.name: var.assignment for var in csp.variables  # type: ignore[union-attr]
            }
            result.success = True
            return True

        # Choose variable using MRV
        var = mrv_variable(unassigned)
        if var is None:
            return False

        # Try each domain value deterministically (sorted for predictability)
        values = sorted(var.domain, key=lambda v: (v if isinstance(v, str) else str(v)))

        for value in values:
            # Assign
            csp.assign(var, value)
            var.assignment = value
            result.assignments[var.name] = value

            # Check constraints
            if csp.consistent():
                # Recurse
                if recurse():
                    return True

            # Backtrack
            csp.unassign(var)
            var.assignment = None
            result.backtrack_count += 1

        return False

    # --- Reset and run ---
    csp.reset_constraints_checked()
    found = recurse()
    print(f'DEBUG: after recurse, csp.constraints_checked={csp.constraints_checked}, found={found}, result.success={result.success}')

    # Copy accumulated constraint count from CSP
    result.constraints_checked = csp.constraints_checked
    print(f'DEBUG: after assignment, result.constraints_checked={result.constraints_checked}')

    # --- Post-processing ---
    if found and result.success:
        # Build ordered_selected_skills via topological sort respecting prerequisites
        assigned_skills = set(result.assignments.keys())
        if prerequisites is not None:
            result.ordered_selected_skills = topological_sort(
                assigned_skills, prerequisites
            )
        else:
            result.ordered_selected_skills = sorted(result.assignments.keys())

        # Verify required skills are all present in the final solution
        if required is not None:
            covered = [s for s in required if s in result.assignments]
            if len(covered) < len(required):
                result.success = False
                result.failure_reason = (
                    f"Not all required skills found in solution. "
                    f"Missing: {set(required) - set(result.assignments.keys())}"
                )
                result.ordered_selected_skills = []
        else:
            result.failure_reason = None
    else:
        result.success = False
        result.failure_reason = (
            "No valid assignment found — constraints unsatisfiable with given domains"
        )
        result.ordered_selected_skills = []

    return result