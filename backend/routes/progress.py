"""Learning progress API routes for MathForStudent."""

from flask import Blueprint, jsonify, request
from flask_login import current_user

from backend.extensions import db
from backend.models import LearningProgress
from backend.security.decorators import login_required_api


progress_bp = Blueprint("progress", __name__)


@progress_bp.get("/")
@login_required_api
def get_progress():
    """Return progress records belonging to the authenticated student."""

    records = LearningProgress.query.filter_by(
        user_id=current_user.id
    ).order_by(
        LearningProgress.last_activity.desc()
    ).all()

    return jsonify({
        "status": "success",
        "progress": [record.to_dict() for record in records],
    }), 200


@progress_bp.post("/")
@login_required_api
def update_progress():
    """Create or increment the student's subject progress."""

    data = request.get_json(silent=True) or {}
    subject = data.get("subject")

    if not isinstance(subject, str):
        return jsonify({
            "status": "error",
            "message": "A valid subject is required.",
        }), 400

    subject = " ".join(subject.strip().lower().split())

    allowed_subjects = {
        "mathematics",
        "physics",
        "chemistry",
        "computer science",
    }

    if subject not in allowed_subjects:
        return jsonify({
            "status": "error",
            "message": "Select a valid subject.",
        }), 400

    record = LearningProgress.query.filter_by(
        user_id=current_user.id,
        subject=subject,
    ).first()

    try:
        if record is None:
            record = LearningProgress(
                user_id=current_user.id,
                subject=subject,
                questions_solved=1,
            )
            db.session.add(record)
        else:
            record.questions_solved += 1

        db.session.commit()

    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Progress could not be saved.",
        }), 500

    return jsonify({
        "status": "success",
        "message": "Learning progress updated.",
        "progress": record.to_dict(),
    }), 200