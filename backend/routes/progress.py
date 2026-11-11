from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from ..models import LearningProgress


progress_bp = Blueprint(
    "progress",
    __name__,
    url_prefix="/api/progress"
)


@progress_bp.route("/", methods=["GET"])
@login_required
def get_progress():
    """Return the logged-in student's learning progress."""

    records = LearningProgress.query.filter_by(
        user_id=current_user.id
    ).order_by(
        LearningProgress.last_studied.desc()
    ).all()

    return jsonify({
        "status": "success",
        "progress": [
            {
                "id": item.id,
                "subject": item.subject,
                "topic": item.topic,
                "questions_answered": item.questions_answered,
                "correct_answers": item.correct_answers,
                "last_studied": (
                    item.last_studied.isoformat()
                    if item.last_studied else None
                )
            }
            for item in records
        ]
    }), 200
