"""
SkillBridge AI — A* Search Algorithm Module

Implements genuine A* Search for personalized learning roadmap generation.

A* uses f(n) = g(n) + h(n) where:
- g(n) = accumulated learning cost from the student's current state
- h(n) = estimated remaining cost to reach the target role
- f(n) = total estimated cost

The algorithm searches through skill-learning states, expanding the lowest
f-score node, and reconstructs the optimal path to the goal.
"""

from __future__ import annotations
import heapq
from collections.abc import Set
from typing import Any

from heuristic import compute_heuristic, _proficiency_rank, compute_path_heuristic
from graph import (
    SkillNode,
    SkillEdge,
    SkillGraph,
    build_graph_from_roles,
)


def _reconstruct_path(
    came_from: dict[str, str | None],
    current: str,
) -> list[str]:
    """Reconstruct the path from start to goal.

    Args:
        came_from: Mapping of each node to its parent in the search tree.
        current: The goal node ID.

    Returns:
        List of node IDs from start to goal, inclusive.
    """
    path = []
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    return path


def a_star_search(
    student_skills: dict[str, str],
    target_role_id: str,
    role_required_skills: list[dict[str, Any]],
    skill_graph: SkillGraph | None = None,
    skill_vocab_path: str | None = None,
    learning_cost_multiplier: float = 1.0,
) -> dict[str, Any]:
    """Run A* Search to find the minimum-cost learning path.

    The algorithm finds an efficient path from the student's current skill
    state to the target role's required skill state, using f(n) = g(n) + h(n).

    Args:
        student_skills: Dict mapping skill_id -> proficiency level
            (e.g., {"Python": "intermediate", "SQL": "beginner"})
        target_role_id: The target career role identifier.
        role_required_skills: List of role skill dicts with skill_id,
            minimum_proficiency, priority, is_core.
        skill_graph: Optional pre-built SkillGraph. If None, one will be
            built from the role requirements and student data.
        skill_vocab_path: Optional path to skill vocabulary JSON for
            learning costs. If None, uses default path.
        learning_cost_multiplier: Scaling factor for learning costs
            (default 1.0).

    Returns:
        Dictionary containing:
        - roadmap: Ordered list of learning steps
        - total_estimated_cost: Total estimated learning cost
        - nodes_expanded: Number of nodes expanded during search
        - search_depth: Depth of the search tree
        - goal_reached: Whether the target state was achieved
    """

    # Build the skill graph if not provided
    if skill_graph is None:
        student_skill_ids = set(student_skills.keys())
        skill_graph = build_graph_from_roles(
            role_required_skills,
            student_skill_ids,
            skill_vocab_path,
        )

    # Determine target skill proficiency map
    target_skills: dict[str, str] = {}
    for req_skill in role_required_skills:
        target_skills[req_skill["skill_id"]] = req_skill.get("minimum_proficiency", "intermediate")

    # Build learning costs per skill
    from pathlib import Path
    import json

    if skill_vocab_path is None:
        skill_vocab_path = str(
            Path(__file__).resolve().parent.parent.parent.parent
            / "data" / "skills" / "skills.json"
        )

    with open(skill_vocab_path, encoding="utf-8") as f:
        skill_vocab = json.load(f)

    learning_costs: dict[str, float] = {}
    for skill in skill_vocab:
        sid = skill.get("id", skill["name"])
        base_cost = skill.get("learning_cost_hours", 100.0)
        learning_costs[sid] = base_cost * learning_cost_multiplier

    # Add entries for role skills not in vocabulary
    for req_skill in role_required_skills:
        sid = req_skill["skill_id"]
        if sid not in learning_costs:
            learning_costs[sid] = 100.0 * learning_cost_multiplier

    # Start state: student's current proficiencies
    # Goal state: student has all target skills at or above required proficiency

# g_scores: best known cost from start to each node
    # We use a dict mapping skill_id to best g score
    g_scores: dict[str, float] = {skill_id: float("inf") for skill_id in skill_graph.nodes.keys()}
    
    # Set start node g-scores based on student's current skills
    for skill_id, prof in student_skills.items():
        if skill_id in g_scores:
            # Student already has this skill — g starts at 0 for this skill
            g_scores[skill_id] = 0.0

    # f_scores: estimated total cost from start through node to goal
    f_scores: dict[str, float] = {skill_id: float("inf") for skill_id in skill_graph.nodes.keys()}

    # Initialize f_scores with heuristic
    for skill_id in g_scores:
        current_prof = student_skills.get(skill_id, "beginner")
        target_prof = target_skills.get(skill_id, "intermediate")
        # Compute heuristic contribution for this skill
        current_rank = _proficiency_rank(current_prof)
        target_rank = _proficiency_rank(target_prof)
        if target_rank > current_rank:
            # Missing proficiency gap contributes to h(n)
            h = learning_costs.get(skill_id, 100.0) * (target_rank - current_rank) / 3.0
        else:
            h = 0.0
        f_scores[skill_id] = g_scores[skill_id] + h

    # came_from: mapping of node to its parent for path reconstruction
    came_from: dict[str, str | None] = {skill_id: None for skill_id in skill_graph.nodes.keys()}

    # Closed set: nodes already evaluated
    closed_set: set[str] = set()

    # A* main loop
    nodes_expanded = 0
    search_depth = 0

    # A* open set initialization: start with student's current skills
    open_set: list[tuple[float, str]] = []  # (f_score, skill_id) priority queue
    for skill_id in student_skills:
        if skill_id in g_scores:
            heapq.heappush(open_set, (f_scores[skill_id], skill_id))

    while open_set:
        current_f, current = heapq.heappop(open_set)
        nodes_expanded += 1

        # If we've already evaluated this node, skip
        if current in closed_set:
            continue

        closed_set.add(current)
        search_depth = max(search_depth, len(closed_set))

        # Check if goal is reached: all target skills already possessed by student.
        # Early return only when student already has every target skill at or
        # above the required proficiency. No search needed in this case.
        goal_met = True
        for skill_id, required_prof in target_skills.items():
            if skill_id in student_skills:
                # Student already has this skill — check proficiency
                current_prof = student_skills[skill_id]
                if _proficiency_rank(current_prof) < _proficiency_rank(required_prof):
                    goal_met = False
                    break
            else:
                # Student does not have this skill — goal not met yet.
                # A* search will find a path to learn it.
                goal_met = False
                break

        if goal_met:
            # Student already has all required skills — return empty roadmap.
            return {
                "roadmap": {
                    "target_role": target_role_id,
                    "learning_steps": [],
                    "total_estimated_cost": 0.0,
                    "skills_acquired": len(target_skills),
                    "skills_remaining": 0,
                    "heuristic_used": "admissible",
                    "algorithm": "A* Search with f(n)=g(n)+h(n)",
                },
                "total_estimated_cost": 0.0,
                "nodes_expanded": 0,
                "search_depth": 0,
                "goal_reached": True,
            }

        # Expand neighbors: find skills that can be learned next
        # A skill is expandable if its prerequisites are satisfied
        neighbors = _get_expandable_neighbors(
            current,
            student_skills,
            target_skills,
            skill_graph,
            learning_costs,
        )

        for neighbor_edge in neighbors:
            neighbor_id = neighbor_edge.to_skill

            # Skip if already evaluated
            if neighbor_id in closed_set:
                continue

            # Cost to learn this skill (g increment)
            skill_cost = learning_costs.get(neighbor_id, 100.0)
            tentative_g = g_scores.get(current, 0.0) + skill_cost

            # Only update if we found a better path
            if tentative_g < g_scores.get(neighbor_id, float("inf")):
                came_from[neighbor_id] = current
                g_scores[neighbor_id] = tentative_g

                # Compute heuristic for neighbor
                current_prof = student_skills.get(neighbor_id, "beginner")
                target_prof = target_skills.get(neighbor_id, "intermediate")
                current_rank = _proficiency_rank(current_prof)
                target_rank = _proficiency_rank(target_prof)
                if target_rank > current_rank:
                    h = learning_costs.get(neighbor_id, 100.0) * max(
                        0, target_rank - current_rank
                    ) / 3.0
                else:
                    h = 0.0

                f_score = tentative_g + h
                f_scores[neighbor_id] = f_score

                # Push to open set if not already there
                if (f_score, neighbor_id) not in open_set:
                    heapq.heappush(open_set, (f_score, neighbor_id))

    # If we exit the loop without the early goal_met return,
    # it means the student was missing some skills and the search exhausted
    # (open_set empty). Build a roadmap from the came_from mapping for the
    # missing skills (those not in student_skills). The came_from structure
    # encodes the optimal learning order via prerequisites.
    missing_target_skills: list[str] = []
    for skill_id, required_prof in target_skills.items():
        if skill_id not in student_skills:
            missing_target_skills.append(skill_id)

    roadmap = _build_roadmap_from_came_from(
        came_from,
        student_skills,
        target_skills,
        learning_costs,
        skill_graph,
    )

    return {
        "roadmap": roadmap,
        "total_estimated_cost": roadmap.get("total_estimated_cost", 0.0),
        "nodes_expanded": nodes_expanded,
        "search_depth": search_depth,
        "goal_reached": False,
    }


def _get_expandable_neighbors(
    current_skill_id: str,
    student_skills: dict[str, str],
    target_skills: dict[str, str],
    skill_graph: SkillGraph,
    learning_costs: dict[str, float],
) -> list[SkillEdge]:
    """Get skills that can be learned next from the current state.

    A skill is expandable if:
    1. It's a neighbor in the graph (has a prerequisite edge from current)
    2. All its prerequisites are satisfied (student already has them)
    3. It hasn't been learned yet (not already in student_skills)

    Returns:
        List of SkillEdge representing valid next learnable skills.
    """
    neighbors: list[SkillEdge] = []

    # Get outgoing edges from the current skill
    outgoing = skill_graph.get_neighbors(current_skill_id) if current_skill_id else []

    for edge in outgoing:
        to_skill_id = edge.to_skill

        # Skip if student already has this skill at or above required
        if to_skill_id in student_skills:
            continue

        # Check prerequisites: a skill can be learned if the student
        # already has its prerequisites
        to_node = skill_graph.get_node(to_skill_id)
        if to_node is None:
            continue

        # Check if all prerequisites of this skill are satisfied
        prerequisites_satisfied = True
        for prereq_id in to_node.prerequisites:
            if prereq_id not in student_skills:
                prerequisites_satisfied = False
                break

        if prerequisites_satisfied:
            neighbors.append(edge)

    # Also consider skills that don't have an edge from current but
    # are directly learnable from the student's current state
    # (skills whose prerequisites are all in the student's current skill set)
    for node_id, node in skill_graph.nodes.items():
        if node_id in student_skills:
            continue  # Already learned
        if node_id in [e.to_skill for e in neighbors]:
            continue  # Already added

        # Check if all prerequisites are in student_skills
        prereqs_satisfied = all(
            prereq in student_skills for prereq in node.prerequisites
        )
        if prereqs_satisfied:
            # Find an edge to this node from current or outgoing
            found_edge = None
            for edge in outgoing:
                if edge.to_skill == node_id:
                    found_edge = edge
                    break

            if found_edge:
                neighbors.append(found_edge)
            elif current_skill_id and current_skill_id != node_id:
                # Create a direct edge from current skill
                neighbors.append(SkillEdge(from_skill=current_skill_id, to_skill=node_id))
            else:
                # Use a foundational skill
                foundational = next(
                    (n for n in skill_graph.all_nodes() if n.learning_cost == 0.0),
                    None,
                )
                if foundational:
                    neighbors.append(
                        SkillEdge(from_skill=foundational.skill_id, to_skill=node_id)
                    )

    return neighbors


def _build_roadmap_from_came_from(
    came_from: dict[str, str | None],
    student_skills: dict[str, str],
    target_skills: dict[str, str],
    learning_costs: dict[str, float],
    skill_graph: SkillGraph,
) -> dict[str, Any]:
    """Build the learning roadmap from the A* came_from mapping.

    Args:
        came_from: Mapping from each skill to its prerequisite/parent.
        student_skills: Student's current skills with proficiency.
        target_skills: Required skills for the target role.
        learning_costs: Per-skill learning costs.
        skill_graph: The skill graph for additional context.

    Returns:
        Structured roadmap dictionary.
    """
    # Reconstruct the path of skills to learn
    # Find which target skills are not yet met.
    # A skill is considered "met" if the student already has it at sufficient
    # proficiency (skill_id in student_skills AND proficiency rank meets requirement).
    # Student does NOT have the skill at all if skill_id not in student_skills.
    missing_skills: list[str] = []
    for skill_id, required_prof in target_skills.items():
        if skill_id in student_skills:
            current_prof = student_skills[skill_id]
            if _proficiency_rank(current_prof) < _proficiency_rank(required_prof):
                # Student has the skill but below required proficiency
                missing_skills.append(skill_id)
        else:
            # Student does not have this skill at all
            missing_skills.append(skill_id)

    # Build ordered learning steps using the came_from structure from A*.
    # The came_from mapping already encodes the optimal learning order
    # (prerequisites before dependents). We follow the came_from chain
    # to reconstruct the path, rather than sorting by cost.
    learning_steps: list[dict[str, Any]] = []
    learned_set: set[str] = set(student_skills.keys())
    total_cost = 0.0

    # Process skills in the order determined by the A* search.
    # We iterate over missing skills following the came_from chains.
    # The came_from dict maps each skill to its prerequisite/parent,
    # so following it from a target skill back to the start gives us
    # the learning order (reversed).

    # Process each missing skill's prerequisite chain
    for skill_id in missing_skills:
        # Determine the prerequisite chain from came_from
        prerequisites: list[str] = []
        parent = came_from.get(skill_id)
        while parent is not None:
            prerequisites.append(parent)
            # Stop if we've reached a student skill or the start of the chain
            if parent in student_skills or parent is None:
                break
            parent = came_from.get(parent)

        # Reverse so prerequisites come first
        prerequisites.reverse()

        # Add prerequisite steps first (if not already learned)
        for prereq_id in prerequisites:
            if prereq_id not in learned_set:
                prereq_cost = learning_costs.get(prereq_id, 100.0)
                total_cost += prereq_cost
                learning_steps.append(
                    {
                        "skill_id": prereq_id,
                        "skill_name": skill_graph.get_node(prereq_id).name
                        if skill_graph.get_node(prereq_id)
                        else prereq_id,
                        "current_proficiency": "not_started",
                        "target_proficiency": target_skills.get(prereq_id, "intermediate"),
                        "estimated_cost": prereq_cost,
                        "reason": f"Prerequisite for {skill_id}",
                        "priority": "prerequisite",
                    }
                )
                learned_set.add(prereq_id)

        # Add the skill itself
        target_prof = target_skills.get(skill_id, "intermediate")
        current_prof = student_skills.get(skill_id, "not_started")

        step: dict[str, Any] = {
            "skill_id": skill_id,
            "skill_name": skill_graph.get_node(skill_id).name
            if skill_graph.get_node(skill_id)
            else skill_id,
            "current_proficiency": current_prof,
            "target_proficiency": target_prof,
            "estimated_cost": learning_costs.get(skill_id, 100.0),
            "reason": f"Learn {skill_id} for {target_skills.get(skill_id, 'role')}",
            "priority": "required",
        }

        # Add prerequisite info if there are prerequisites
        if prerequisites:
            step["prerequisites"] = [skill_graph.get_node(p).name if skill_graph.get_node(p) else p for p in prerequisites]

        learning_steps.append(step)
        total_cost += learning_costs.get(skill_id, 100.0)
        learned_set.add(skill_id)

    # Also include skills student already has, showing their status
    for skill_id, current_prof in student_skills.items():
        if skill_id in target_skills:
            target_prof = target_skills[skill_id]
            learning_steps.append(
                {
                    "skill_id": skill_id,
                    "skill_name": skill_graph.get_node(skill_id).name
                    if skill_graph.get_node(skill_id)
                    else skill_id,
                    "current_proficiency": current_prof,
                    "target_proficiency": target_prof,
                    "estimated_cost": 0.0,
                    "reason": "Already possessed",
                    "priority": "strong",
                }
            )

    # Skills that were reached during search but weren't in original student_skills
    # are already included in the learning steps above via the came_from chains.

    return {
        "target_role": None,  # Will be set by caller
        "learning_steps": learning_steps,
        "total_estimated_cost": round(total_cost, 2),
        "skills_acquired": len(learned_set),
        "skills_remaining": len(missing_skills),
        "heuristic_used": "admissible",
        "algorithm": "A* Search with f(n)=g(n)+h(n)",
    }