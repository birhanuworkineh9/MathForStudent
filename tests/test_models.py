from backend.app import create_app
from backend.extensions import db
from backend.models import User, Question, LearningProgress
from backend.security.validation import (
    validate_question,
    validate_registration
)


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "/tmp/mathforstudent-test"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    OPENAI_API_KEY = None
    OPENAI_MODEL = "gpt-4.1-mini"


def test_user_password():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        user = User(
            full_name="Test Student",
            email="student@example.com"
        )
        user.set_password("A-long-test-password-123")

        assert user.check_password("A-long-test-password-123")
        assert not user.check_password("wrong-password")

        db.drop_all()


def test_question_validation():
    valid, error = validate_question(
        "mathematics",
        "Solve 2x + 5 = 15"
    )
    assert valid is True
    assert error is None


def test_registration_validation():
    valid, error = validate_registration(
        "Test Student",
        "student@example.com",
        "A-long-test-password-123"
    )
    assert valid is True
    assert error is None