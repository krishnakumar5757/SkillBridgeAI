"""Focused tests for the Module 3 A* integration boundary."""

from app.services.module3_learning import _to_astar_vocabulary_keys


class _SkillLookup:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *_):
        return self

    def all(self):
        return self.rows


class _FakeDb:
    def query(self, *_):
        return _SkillLookup([("skill-python-id", "Python")])


def test_astar_adapter_maps_known_skill_uuid_to_canonical_name():
    skill_id = "skill-python-id"

    student_skills, role_skills = _to_astar_vocabulary_keys(
        _FakeDb(),
        {skill_id: "intermediate"},
        [{"skill_id": skill_id, "skill_name": "Python", "minimum_proficiency": "intermediate"}],
    )

    assert student_skills == {"Python": "intermediate"}
    assert role_skills[0]["skill_id"] == "Python"


def test_astar_adapter_preserves_unresolved_skill_name_for_existing_fallback():
    _, role_skills = _to_astar_vocabulary_keys(
        _FakeDb(),
        {},
        [{"skill_id": "unknown-skill-id", "skill_name": "Unknown Skill"}],
    )

    assert role_skills[0]["skill_id"] == "Unknown Skill"
