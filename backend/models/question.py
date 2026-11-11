from datetime import datetime, timezone
from ..extensions import db


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    subject = db.Column(
        db.String(50),
        nullable=False
    )

    question_text = db.Column(
        db.Text,
        nullable=False
    )

    image_path = db.Column(
        db.String(500),
        nullable=True
    )

    answer = db.Column(
        db.Text,
        nullable=True
    )

    explanation = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="questions"
    )

    def __repr__(self):
        return f"<Question {self.id}: {self.subject}>"
