"""
SkillBridge AI — A* Search Graph Module

Represents the skill learning graph for A* search.
Nodes are skills with learning costs and prerequisite constraints.
Edges represent valid learning transitions.
"""

from __future__ import annotations

from typing import Any


class SkillNode:
    """A node in the skill learning graph."""

    def __init__(
        self,
        skill_id: str,
        name: str,
        category: str | None,
        learning_cost: float,
        prerequisites: list[str] | None = None,
    ):
        self.skill_id = skill_id
        self.name = name
        self.category = category
        self.learning_cost = learning_cost
        self.prerequisites = prerequisites if prerequisites else []

    def __repr__(self):
        return f"SkillNode({self.skill_id}:{self.name})"


class SkillEdge:
    """An edge in the skill learning graph representing a valid transition."""

    def __init__(self, from_skill: str, to_skill: str):
        self.from_skill = from_skill
        self.to_skill = to_skill

    def __repr__(self):
        return f"SkillEdge({self.from_skill} -> {self.to_skill})"


class SkillGraph:
    """Directed graph of skills for A* search.

    Nodes: skill_id -> SkillNode
    Edges: skill_id -> list of SkillEdge (outgoing transitions)

    The graph respects prerequisite constraints: a skill edge from A to B
    is only valid if A is already "learned" (in the student's current state).
    """

    def __init__(self, nodes: dict[str, SkillNode], edges: dict[str, list[SkillEdge]] | None = None):
        self.nodes: dict[str, SkillNode] = nodes
        # edges[skill_id] = list of SkillEdge representing skills that can be learned next
        self.edges: dict[str, list[SkillEdge]] = edges if edges else {}

    def add_node(self, node: SkillNode):
        self.nodes[node.skill_id] = node

    def add_edge(self, from_skill_id: str, to_skill_id: str, edge: SkillEdge):
        if from_skill_id not in self.edges:
            self.edges[from_skill_id] = []
        self.edges[from_skill_id].append(edge)

    def get_node(self, skill_id: str) -> SkillNode | None:
        return self.nodes.get(skill_id)

    def get_neighbors(self, skill_id: str) -> list[SkillEdge]:
        """Get valid outgoing edges from a skill node.

        Returns edges where the prerequisite is satisfied (the from_skill
        is in the learned set). The caller must check prerequisites.
        """
        return self.edges.get(skill_id, [])

    def has_node(self, skill_id: str) -> bool:
        return skill_id in self.nodes

    def all_nodes(self) -> list[SkillNode]:
        return list(self.nodes.values())


def build_graph_from_roles(
    role_required_skills: list[dict[str, Any]],
    student_skill_ids: set[str],
    skill_vocab_path: str | None = None,
) -> SkillGraph:
    """Build a skill learning graph from role requirements and student data.

    Args:
        role_required_skills: List of role skill dicts with skill_id,
            minimum_proficiency, priority, is_core, and optional skill_name.
        student_skill_ids: Set of skill_ids the student already has.
        skill_vocab_path: Optional path to skill vocabulary JSON for learning costs.

    Returns:
        SkillGraph representing valid learning transitions.
    """
    import json
    from pathlib import Path

    # Load skill vocabulary for learning costs
    if skill_vocab_path is None:
        skill_vocab_path = str(
            Path(__file__).resolve().parent.parent.parent.parent
            / "data" / "skills" / "skills.json"
        )

    with open(skill_vocab_path, encoding="utf-8") as f:
        skill_vocab = json.load(f)

    # Build skill name/alias lookup
    skill_name_map: dict[str, str] = {}
    for skill in skill_vocab:
        skill_name_map[skill["name"].lower()] = skill["name"]
        for alias in skill.get("aliases", []):
            skill_name_map[alias.lower()] = skill["name"]

    # Build nodes for all skills the student can learn
    # Include: role required skills + student's current skills
    nodes: dict[str, SkillNode] = {}

    # Add student's current skills as nodes with cost 0 (already learned)
    for sid in student_skill_ids:
        # Try to find the skill in the vocabulary
        skill_entry = None
        for sk in skill_vocab:
            sid_from_vocab = sk.get("id", sk["name"])
            if sid_from_vocab == sid or sk["name"].lower() == sid.lower():
                skill_entry = sk
                break
        # Also check aliases
        if skill_entry is None:
            for sk in skill_vocab:
                for alias in sk.get("aliases", []):
                    if alias.lower() == sid.lower():
                        skill_entry = sk
                        break

        cost = 0.0 if skill_entry else 1.0  # 0 cost if we know it, 1 as fallback
        name = skill_entry.get("name", sid) if skill_entry else sid
        category = skill_entry.get("category") if skill_entry else None
        nodes[sid] = SkillNode(
            skill_id=sid,
            name=name,
            category=category,
            learning_cost=cost,
        )

    # Add role required skills as learnable nodes
    for req_skill in role_required_skills:
        skill_id = req_skill["skill_id"]
        min_prof = req_skill.get("minimum_proficiency", "intermediate")

        # Determine learning cost based on student's current proficiency
        if skill_id in student_skill_ids:
            # Student already has this skill - cost 0 (review/maintenance)
            cost = 0.0
        else:
            # Student doesn't have it - use vocabulary cost
            skill_entry = None
            for sk in skill_vocab:
                sid_from_vocab = sk.get("id", sk["name"])
                if sk["name"].lower() == skill_id.lower() or sid_from_vocab == skill_id:
                    skill_entry = sk
                    break
                for alias in sk.get("aliases", []):
                    if alias.lower() == skill_id.lower():
                        skill_entry = sk
                        break

            if skill_entry:
                # Base cost from vocabulary, scaled by proficiency gap
                base_cost = skill_entry.get("learning_cost_hours", 100.0)
                # Higher proficiency requirement = higher effective cost
                prof_scale = {"beginner": 1.0, "intermediate": 1.5, "advanced": 2.0}
                cost = base_cost * prof_scale.get(min_prof, 1.5)
            else:
                # Default cost for unknown skill
                cost = 100.0

        name = req_skill.get("skill_name", skill_id)
        category = req_skill.get("category")

        nodes[skill_id] = SkillNode(
            skill_id=skill_id,
            name=name,
            category=category,
            learning_cost=cost,
        )

    # Build edges: prerequisite relationships
    # For each skill, add edges from its prerequisites to it
    edges: dict[str, list[SkillEdge]] = {}

    # Also add edges for skills the student doesn't have yet,
    # from skills they do have (or from foundational skills)
    all_skill_ids = set(nodes.keys())

    for skill_id, node in nodes.items():
        # Get prerequisites from the role data or vocabulary
        prereq_ids: list[str] = []

        # Check if this skill has prerequisites in the role data
        for req_skill in role_required_skills:
            if req_skill["skill_id"] == skill_id:
                # The role may have dependency info; if not, we'll use
                # a simple rule: earlier skills in the list are prerequisites
                break

        # If no explicit prerequisites from role data, use vocabulary
        if not prereq_ids and skill_id in skill_name_map:
            # Try to find prerequisite info
            for sk in skill_vocab:
                if sk["name"].lower() == skill_id.lower() or sk["id"] == skill_id:
                    prereq_ids = sk.get("prerequisites", [])
                    break

        # Add edges from prerequisites to this skill
        for prereq_id in prereq_ids:
            if prereq_id in all_skill_ids and skill_id != prereq_id:
                if prereq_id not in edges:
                    edges[prereq_id] = []
                edges[prereq_id].append(SkillEdge(from_skill=prereq_id, to_skill=skill_id))

        # Also add edges from student's current skills to missing required skills
        # This allows A* to start from the student's current state
        for sid in student_skill_ids:
            if sid != skill_id and skill_id not in student_skill_ids:
                # Student can start learning from their current position
                if sid not in edges:
                    edges[sid] = []
                # Check if this edge already exists
                existing = [e for e in edges[sid] if e.to_skill == skill_id]
                if not existing:
                    edges[sid].append(SkillEdge(from_skill=sid, to_skill=skill_id))

    return SkillGraph(nodes=nodes, edges=edges)