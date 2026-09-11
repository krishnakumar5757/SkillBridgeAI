"""
SkillBridge AI — Module 1 API Tests
"""
from __future__ import annotations

import pytest
from fastapi import status
from app.core.database import Base
from app.models.skill import Skill


def test_create_student_profile(client):
    """Test creating a student profile."""
    profile_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "1234567890",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "address": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "Testland",
    }
    response = client.post("/api/v1/profile", json=profile_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == profile_data["email"]
    assert data["first_name"] == profile_data["first_name"]
    assert data["last_name"] == profile_data["last_name"]


def test_get_student_profile(client):
    """Test getting a student profile by ID."""
    # First create a profile
    profile_data = {
        "email": "test2@example.com",
        "first_name": "Test2",
        "last_name": "User2",
        "phone_number": "0987654321",
        "date_of_birth": "2000-02-02",
        "gender": "Female",
        "address": "456 Test Ave",
        "city": "Test City",
        "state": "TS",
        "zip_code": "54321",
        "country": "Testland",
    }
    create_resp = client.post("/api/v1/profile", json=profile_data)
    student_id = create_resp.json()["id"]

    # Now get the profile
    response = client.get(f"/api/v1/profile/{student_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == student_id
    assert data["email"] == profile_data["email"]


def test_get_nonexistent_student_profile(client):
    """Test getting a nonexistent student profile."""
    nonexistent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/profile/{nonexistent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_academic_info(client):
    """Test creating academic information for a student."""
    # First create a student profile
    profile_data = {
        "email": "test3@example.com",
        "first_name": "Test3",
        "last_name": "User3",
        "phone_number": "1111111111",
        "date_of_birth": "2000-03-03",
        "gender": "Male",
        "address": "789 Test Rd",
        "city": "Test City",
        "state": "TS",
        "zip_code": "11111",
        "country": "Testland",
    }
    profile_resp = client.post("/api/v1/profile", json=profile_data)
    student_id = profile_resp.json()["id"]

    academic_data = {
        "institution": "Test University",
        "degree": "Bachelor of Science",
        "field_of_study": "Computer Science",
        "graduation_year": 2023,
        "gpa": 3.5,
    }
    response = client.post(f"/api/v1/academic-info?student_id={student_id}", json=academic_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["student_id"] == student_id
    assert data["institution"] == academic_data["institution"]
    assert data["degree"] == academic_data["degree"]


def test_get_academic_info_list(client):
    """Test getting a list of academic information for a student."""
    # Create a student profile
    profile_data = {
        "email": "test4@example.com",
        "first_name": "Test4",
        "last_name": "User4",
        "phone_number": "2222222222",
        "date_of_birth": "2000-04-04",
        "gender": "Female",
        "address": "321 Test Blvd",
        "city": "Test City",
        "state": "TS",
        "zip_code": "22222",
        "country": "Testland",
    }
    profile_resp = client.post("/api/v1/profile", json=profile_data)
    student_id = profile_resp.json()["id"]

    # Create two academic info records
    academic_data1 = {
        "institution": "Test University",
        "degree": "Bachelor of Science",
        "field_of_study": "Computer Science",
        "graduation_year": 2023,
        "gpa": 3.5,
    }
    academic_data2 = {
        "institution": "Test College",
        "degree": "Associate of Arts",
        "field_of_study": "General Studies",
        "graduation_year": 2021,
        "gpa": 3.8,
    }
    client.post(f"/api/v1/academic-info?student_id={student_id}", json=academic_data1)
    client.post(f"/api/v1/academic-info?student_id={student_id}", json=academic_data2)

    # Get the list
    response = client.get(f"/api/v1/academic-info/{student_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["student_id"] == student_id
    assert data[1]["student_id"] == student_id


def test_create_academic_info_invalid_student(client):
    """Test creating academic information for a nonexistent student."""
    nonexistent_id = "00000000-0000-0000-0000-000000000000"
    academic_data = {
        "institution": "Test University",
        "degree": "Bachelor of Science",
        "field_of_study": "Computer Science",
        "graduation_year": 2023,
        "gpa": 3.5,
    }
    response = client.post(f"/api/v1/academic-info?student_id={nonexistent_id}", json=academic_data)
    # The service raises ValueError for nonexistent student, which the route turns into 400
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_interest(client):
    """Test creating an interest for a student."""
    # First create a student profile
    profile_data = {
        "email": "test5@example.com",
        "first_name": "Test5",
        "last_name": "User5",
        "phone_number": "3333333333",
        "date_of_birth": "2000-05-05",
        "gender": "Male",
        "address": "654 Test Ln",
        "city": "Test City",
        "state": "TS",
        "zip_code": "33333",
        "country": "Testland",
    }
    profile_resp = client.post("/api/v1/profile", json=profile_data)
    student_id = profile_resp.json()["id"]

    interest_data = {
        "name": "Robotics",
    }
    response = client.post(f"/api/v1/interests?student_id={student_id}", json=interest_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["student_id"] == student_id
    assert data["name"] == interest_data["name"]


def test_get_interests_list(client):
    """Test getting a list of interests for a student."""
    # Create a student profile
    profile_data = {
        "email": "test6@example.com",
        "first_name": "Test6",
        "last_name": "User6",
        "phone_number": "4444444444",
        "date_of_birth": "2000-06-06",
        "gender": "Female",
        "address": "987 Test Pl",
        "city": "Test City",
        "state": "TS",
        "zip_code": "44444",
        "country": "Testland",
    }
    profile_resp = client.post("/api/v1/profile", json=profile_data)
    student_id = profile_resp.json()["id"]

    # Create two interest records
    interest_data1 = {"name": "Chess"}
    interest_data2 = {"name": "Painting"}
    client.post(f"/api/v1/interests?student_id={student_id}", json=interest_data1)
    client.post(f"/api/v1/interests?student_id={student_id}", json=interest_data2)

    # Get the list
    response = client.get(f"/api/v1/interests/{student_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["student_id"] == student_id
    assert data[1]["student_id"] == student_id


def test_create_project(client):
    """Test creating a project for a student."""
    # First create a student profile
    profile_data = {
        "email": "test7@example.com",
        "first_name": "Test7",
        "last_name": "User7",
        "phone_number": "5555555555",
        "date_of_birth": "2000-07-07",
        "gender": "Male",
        "address": "147 Test Way",
        "city": "Test City",
        "state": "TS",
        "zip_code": "55555",
        "country": "Testland",
    }
    profile_resp = client.post("/api/v1/profile", json=profile_data)
    student_id = profile_resp.json()["id"]

    project_data = {
        "title": "Test Project",
        "description": "A test project",
        "technologies": "Python, FastAPI",
    }
    response = client.post(f"/api/v1/projects?student_id={student_id}", json=project_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["student_id"] == student_id
    assert data["title"] == project_data["title"]
    assert data["description"] == project_data["description"]


def test_get_projects_list(client):
    """Test getting a list of projects for a student."""
    # Create a student profile
    profile_data = {
        "email": "test8@example.com",
        "first_name": "Test8",
        "last_name": "User8",
        "phone_number": "6666666666",
        "date_of_birth": "2000-08-08",
        "gender": "Female",
        "address": "258 Test Dr",
        "city": "Test City",
        "state": "TS",
        "zip_code": "66666",
        "country": "Testland",
    }
    profile_resp = client.post("/api/v1/profile", json=profile_data)
    student_id = profile_resp.json()["id"]

    # Create two project records
    project_data1 = {
        "title": "Project 1",
        "description": "First project",
        "technologies": "Java, Spring",
    }
    project_data2 = {
        "title": "Project 2",
        "description": "Second project",
        "technologies": "JavaScript, React",
    }
    client.post(f"/api/v1/projects?student_id={student_id}", json=project_data1)
    client.post(f"/api/v1/projects?student_id={student_id}", json=project_data2)

    # Get the list
    response = client.get(f"/api/v1/projects/{student_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["student_id"] == student_id
    assert data[1]["student_id"] == student_id


def test_create_self_reported_skill(client, db_session):
    """Test creating a self-reported skill for a student."""
    # First create a student profile
    profile_data = {
        "email": "test9@example.com",
        "first_name": "Test9",
        "last_name": "User9",
        "phone_number": "7777777777",
        "date_of_birth": "2000-09-09",
        "gender": "Male",
        "address": "369 Test Ct",
        "city": "Test City",
        "state": "TS",
        "zip_code": "77777",
        "country": "Testland",
    }
    profile_resp = client.post("/api/v1/profile", json=profile_data)
    student_id = profile_resp.json()["id"]

    # Ensure the skill exists in the skills table
    skill_id = "Python"
    skill = db_session.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        skill = Skill(id=skill_id, name="Python", category="Programming Language")
        db_session.add(skill)
        db_session.commit()

    skill_data = {
        "skill_id": skill_id,
        "proficiency": "intermediate",
    }
    response = client.post(f"/api/v1/skills/self-reported?student_id={student_id}", json=skill_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["student_id"] == student_id
    assert data["skill_id"] == skill_data["skill_id"]
    assert data["proficiency"] == skill_data["proficiency"]
    assert data["source"] == "self_reported"  # Note: underscore, not hyphen
    assert data["confidence"] == 1.0  # Self-reported skills have confidence 1.0


def test_get_self_reported_skills_list(client, db_session):
    """Test getting a list of self-reported skills for a student."""
    # Create a student profile
    profile_data = {
        "email": "test10@example.com",
        "first_name": "Test10",
        "last_name": "User10",
        "phone_number": "8888888888",
        "date_of_birth": "2000-10-10",
        "gender": "Female",
        "address": "741 Test St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "88888",
        "country": "Testland",
    }
    profile_resp = client.post("/api/v1/profile", json=profile_data)
    student_id = profile_resp.json()["id"]

    # Ensure the skills exist in the skills table
    for skill_id, skill_name in [("Python", "Programming Language"), ("Java", "Programming Language")]:
        skill = db_session.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            skill = Skill(id=skill_id, name=skill_name, category="Programming Language")
            db_session.add(skill)
    db_session.commit()

    # Create two self-reported skill records
    skill_data1 = {
        "skill_id": "Python",
        "proficiency": "intermediate",
    }
    skill_data2 = {
        "skill_id": "Java",
        "proficiency": "beginner",
    }
    client.post(f"/api/v1/skills/self-reported?student_id={student_id}", json=skill_data1)
    client.post(f"/api/v1/skills/self-reported?student_id={student_id}", json=skill_data2)

    # Get the list
    response = client.get(f"/api/v1/skills/{student_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["student_id"] == student_id
    assert data[1]["student_id"] == student_id


def test_create_self_reported_skill_nonexistent_skill(client):
    """Test creating a self-reported skill with a nonexistent skill ID."""
    # First create a student profile
    profile_data = {
        "email": "test11@example.com",
        "first_name": "Test11",
        "last_name": "User11",
        "phone_number": "9999999999",
        "date_of_birth": "2000-11-11",
        "gender": "Male",
        "address": "852 Test Ave",
        "city": "Test City",
        "state": "TS",
        "zip_code": "99999",
        "country": "Testland",
    }
    profile_resp = client.post("/api/v1/profile", json=profile_data)
    student_id = profile_resp.json()["id"]

    # Use a skill ID that likely does not exist in the vocabulary
    skill_data = {
        "skill_id": "NonexistentSkill123",
        "proficiency": "intermediate",
    }
    response = client.post(f"/api/v1/skills/self-reported?student_id={student_id}", json=skill_data)
    # The service might return a 400 or 404 or 500 depending on implementation.
    # We expect a 400 because the skill validation might fail in the service.
    # However, note that the service might still create the skill if it doesn't validate against the vocabulary.
    # We'll check for a 4xx error.
    assert response.status_code >= 400 and response.status_code < 500


def test_missing_required_fields_student_profile(client):
    """Test creating a student profile with missing required fields."""
    # Missing email, first_name, last_name which are required
    incomplete_data = {
        "phone_number": "1234567890",
        "date_of_birth": "2000-01-01",
    }
    response = client.post("/api/v1/profile", json=incomplete_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY  # Validation error


def test_invalid_student_id_format(client):
    """Test accessing an endpoint with an invalid student ID format."""
    # Use an invalid UUID format
    invalid_id = "not-a-uuid"
    response = client.get(f"/api/v1/profile/{invalid_id}")
    # The path parameter is a string, but we expect a UUID. The endpoint might still try to process it.
    # However, the service will likely not find a student with that ID and return 404.
    # But note: the Path parameter does not have a regex for UUID, so it will accept any string.
    # We expect a 404 because no student with that ID exists.
    response = client.get(f"/api/v1/profile/{invalid_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND