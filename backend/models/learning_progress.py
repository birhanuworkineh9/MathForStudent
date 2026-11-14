from datetime import datetime
from backend.extensions import db


class LearningProgress(db.Model):
    __tablename__ = "learning_progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    subject = db.Column(db.String(50), nullable=False)
    questions_solved = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    last_activity = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = db.relationship(
        "User",
        back_populates="progress"
    )