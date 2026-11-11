"""
MathForStudent User Model

Stores student account information securely.
"""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db


class User(UserMixin, db.Model):
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

    education_level = db.Column(
        db.String(50),
        nullable=False,
        default="Grade 9"
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

    learning_progress = db.relationship(
        "LearningProgress",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """Hash and save the user's password."""

        if not isinstance(password, str) or len(password) < 8:
            raise ValueError(
                "Password must contain at least 8 characters."
            )

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a submitted password."""

        if not isinstance(password, str):
            return False

        return check_password_hash(
            self.password_hash,password
        )

    def __repr__(self):
        return f"<User {self.email}>"

