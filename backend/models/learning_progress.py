
"""Learning progress database model."""

from datetime import datetime, timezone

from backend.extensions import db


class LearningProgress(db.Model):
    __tablename__ = "learning_progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    subject = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )

    questions_solved = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    last_activity = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="progress"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "questions_solved": self.questions_solved,
            "last_activity": (
                self.last_activity.isoformat()
                if self.last_activity else None
            )
        }
