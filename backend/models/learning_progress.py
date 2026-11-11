from datetime import datetime, timezone
from ..extensions import db


class LearningProgress(db.Model):
    __tablename__ = "learning_progress"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    subject = db.Column(
        db.String(50),
        nullable=False
    )

    topic = db.Column(
        db.String(150),
        nullable=True
    )

    questions_answered = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    correct_answers = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    last_studied = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="learning_progress"
    )

    def __repr__(self):
        return f"<LearningProgress {self.subject}>"
