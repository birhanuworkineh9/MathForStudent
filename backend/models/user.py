from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash = db.Column(db.String(255), nullable=False)

    education_level = db.Column(
        db.String(50),
        nullable=False,
        default="Grade 9"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )