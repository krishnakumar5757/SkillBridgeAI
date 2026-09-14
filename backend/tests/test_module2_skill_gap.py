"""Focused reliability tests for Skill Gap student validation."""


def _profile(email: str) -> dict[str, str]:
    return {
        "email": email,
        "first_name": "Skill",
        "last_name": "Bridge",
    }


def test_unknown_student_returns_not_found_for_skill_gap(client):
    response = client.post(
        "/api/v1/skill-gap/analyze",
        params={"student_id": "missing-student", "role_id": "software_engineer"},
    )

    assert response.status_code == 404
    assert "not found" in str(response.json()).lower()


def test_existing_student_without_skills_returns_valid_skill_gap(client):
    created = client.post("/api/v1/profile", json=_profile("empty-skills@example.com"))
    assert created.status_code == 201
    student_id = created.json()["id"]

    response = client.post(
        "/api/v1/skill-gap/analyze",
        params={"student_id": student_id, "role_id": "software_engineer"},
    )

    assert response.status_code == 200
    assert response.json()["student_id"] == student_id
    assert response.json()["total_skills_acquired"] == 0
