import pytest

from backend.app import create_app
from backend.extensions import db


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-only-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "/tmp/mathforstudent-test"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    OPENAI_API_KEY = None
    OPENAI_MODEL = "gpt-4.1-mini"


@pytest.fixture
def client():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield client

        db.drop_all()


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200


def test_invalid_subject(client):
    response = client.post(
        "/api/solve",
        data={
            "subject": "biology",
            "question": "What is a cell?"
        }
    )

    assert response.status_code == 400


def test_empty_question(client):
    response = client.post(
        "/api/solve",
        data={
            "subject": "mathematics",
            "question": ""
        }
    )

    assert response.status_code == 400


def test_register(client):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Test Student",
            "email": "test@example.com",
            "password": "A-long-test-password-123"
        }
    )

    assert response.status_code == 201


def test_history_requires_login(client):
    response = client.get("/api/history")
    assert response.status_code == 401