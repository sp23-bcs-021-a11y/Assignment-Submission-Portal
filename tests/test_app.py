
import sqlite3
import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test_submissions.db"

    app = create_app({
        "TESTING": True,
        "DATABASE": str(db_path),
        "SECRET_KEY": "test-secret"
    })

    with app.test_client() as test_client:
        yield test_client


def get_submission_count(client):
    db_path = client.application.config["DATABASE"]

    with sqlite3.connect(db_path) as conn:
        result = conn.execute(
            "SELECT COUNT(*) FROM submissions"
        ).fetchone()

    return result[0]


def test_valid_submission(client):
    response = client.post("/", data={
        "student_name": "Muhammad Sadiq",
        "registration_number": "SP23-BCS-021",
        "assignment_title": "DevOps Lab Mid",
        "submission_url": "https://github.com"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Assignment submitted successfully!" in response.data
    assert b"Muhammad Sadiq" in response.data
    assert get_submission_count(client) == 1


def test_missing_registration_number(client):
    response = client.post("/", data={
        "student_name": "Muhammad Sadiq",
        "registration_number": "",
        "assignment_title": "DevOps Lab Mid",
        "submission_url": "https://github.com"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"All fields are required." in response.data
    assert get_submission_count(client) == 0


def test_invalid_submission_url(client):
    response = client.post("/", data={
        "student_name": "Muhammad Sadiq",
        "registration_number": "SP23-BCS-021",
        "assignment_title": "DevOps Lab Mid",
        "submission_url": "invalid-url"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid submission URL" in response.data
    assert get_submission_count(client) == 0
