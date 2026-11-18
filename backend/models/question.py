
"""Question and solution database model."""

from datetime import datetime, timezone

from backend.extensions import db


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    subject = db.Column(
        db.String(50),
        nullable=False,
        index=True
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
        nullable=False,
        index=True
    )

    user = db.relationship(
        "User",
        back_populates="questions"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "question_text": self.question_text,
            "answer": self.answer,
            "explanation": self.explanation,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            )
        }
