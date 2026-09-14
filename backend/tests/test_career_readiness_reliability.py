"""Focused readiness regression test for matched numeric proficiencies."""

from uuid import uuid4

from app.models.student import Student
from app.services.career_readiness import analyze_career_readiness


def test_readiness_handles_existing_student_with_numeric_proficiency(db_session, monkeypatch):
    student = Student(id=str(uuid4()), first_name="Ready", last_name="Student", email=f"{uuid4()}@example.com")
    db_session.add(student)
    db_session.flush()
    db_session.commit()
    monkeypatch.setattr(
        "app.services.career_readiness.get_student_skills",
        lambda _db, _student_id: {"skill-id": {"skill_name": "Python", "proficiency": 3}},
    )

    response = analyze_career_readiness(
        student.id,
        "software_engineer",
        db=db_session,
    )

    assert response["skills_met"]
    assert response["skills_met"][0]["skill_id"] == "skill-id"
    assert response["skills_met"][0]["skill_name"] == "Python"
    assert response["skills_met"][0]["skill_id"] != response["skills_met"][0]["skill_name"]
    assert response["skills_met"][0]["current_proficiency"] == 3
