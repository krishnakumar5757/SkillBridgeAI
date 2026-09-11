"""Simple plain-Python CSP representation for SkillBridge Module 4.

Contains:
  - CSP model (variables, domains, constraints, assignments)
  - Variable tracking for backtracking search
"""

from __future__ import annotations


class Variable:
    """A CSP variable with a name, domain, and optional assignment."""

    def __init__(self, name: str, domain: list[str]):
        self.name = name
        self.original_domain = list(domain)
        self.domain = list(domain)  # current domain (may be narrowed)
        self.assignment: str | None = None
        self.domain_reduced = False  # track if domain was narrowed during search


class CSP:
    """Constraint Satisfaction Problem with variables, domains, and constraints."""

    def __init__(self):
        self.variables: list[Variable] = []
        self.constraints: list[constraint_function] = []
        self.assignments: dict[str, str] = {}  # name -> assigned value
        self.constraints_checked = 0
        self.backtrack_count = 0

    def add_variable(self, name: str, domain: list[str]) -> Variable:
        """Add a variable with the given name and domain."""
        var = Variable(name, domain)
        self.variables.append(var)
        return var

    def add_constraint(self, constraint: constraint_function) -> None:
        """Add a constraint function. A constraint is a callable:
        constraint(assigned_vars_dict) -> bool | None (None = ok, False = fail)."""
        self.constraints.append(constraint)

    def assign(self, var: Variable, value: str) -> None:
        """Assign a value to a variable."""
        self.assignments[var.name] = value
        var.assignment = value

    def unassign(self, var: Variable) -> None:
        """Remove an assignment from a variable."""
        if var.name in self.assignments:
            del self.assignments[var.name]
        var.assignment = None

    def is_assigned(self, var: Variable) -> bool:
        """Check if a variable has an assignment."""
        return var.assignment is not None

    def consistent(self) -> bool:
        """Check all constraints against current assignments.

        constraints_checked accumulates across calls (reset manually via
        reset_constraints_checked()) so the solver can report an accurate total.
        """
        self._consistent_call_count = getattr(self, '_consistent_call_count', 0) + 1
        assigned = {
            var.name: var.assignment  # type: ignore[union-attr]
            for var in self.variables
            if var.assignment is not None
        }
        for constraint in self.constraints:
            self.constraints_checked += 1
            if not constraint(assigned):
                return False
        return True

    def reset_constraints_checked(self) -> None:
        """Reset the constraint counter — use at the start of a new search."""
        self.constraints_checked = 0


ConstraintFunction = (
    # A constraint is: callable[[dict[str, str]], bool | None]
    # Returns False if constraints are violated, True or None if ok.
)


def prerequisite_constraint(assigned: dict[str, str], prerequisites: dict[str, list[str]]) -> bool:
    """Check that for each skill, its prerequisites are already assigned.

    assigned: mapping skill_name -> selected_level / selected_value
    prerequisites: mapping skill_name -> list of required prerequisite skill names
    """
    for skill, reqs in prerequisites.items():
        if skill in assigned:
            for prereq in reqs:
                if prereq not in assigned:
                    return False
    return True


def required_skills_constraint(
    assigned: dict[str, str], required: set[str], min_count: int = 1
) -> bool:
    """Check that at least `min_count` of the required skills are assigned.

    assigned: mapping skill_name -> selected_level / selected_value
    required: set of skill names that should be present
    """
    covered = [s for s in required if s in assigned]
    return len(covered) >= min_count


def conflicting_skills_constraint(assigned: dict[str, str], conflicting: dict[str, list[str]]) -> bool:
    """Check that no two conflicting skills are assigned simultaneously.

    assigned: mapping skill_name -> selected_level / selected_value
    conflicting: mapping skill_name -> list of skill names that conflict with it
    """
    for skill, conflicts in conflicting.items():
        if skill in assigned:
            for conflict in conflicts:
                if conflict in assigned:
                    return False
    return True


def dependency_validation_constraint(
    assigned: dict[str, str], dependencies: dict[str, list[str]]
) -> bool:
    """Validate that skill dependencies are satisfied.

    assigned: mapping skill_name -> selected_level / selected_value
    dependencies: mapping skill_name -> list of dependency skill names
    """
    for skill, deps in dependencies.items():
        if skill in assigned:
            for dep in deps:
                if dep not in assigned:
                    return False
    return True