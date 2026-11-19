
"""User database model for MathForStudent."""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from backend.extensions import db


class User(UserMixin, db.Model):
    """Database model for student and administrator accounts."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # New accounts are students by default.
    # Administrator roles must be assigned through a trusted process.
    role = db.Column(
        db.String(20),
        nullable=False,
        default="student",
        server_default="student"
    )

    education_level = db.Column(
        db.String(50),
        nullable=False,
        default="Grade 9",
        server_default="Grade 9"
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    questions = db.relationship(
        "Question",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    progress = db.relationship(
        "LearningProgress",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a password against its stored hash."""
        if not isinstance(password, str):
            return False

        return check_password_hash(
            self.password_hash,
            password
        )

    def get_id(self) -> str:
        """Return the user ID for Flask-Login."""
        return str(self.id)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
