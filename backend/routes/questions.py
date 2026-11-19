
"""Question solving and image upload routes."""

from pathlib import Path

from flask import Blueprint, request, jsonify, current_app

from backend.extensions import limiter
from backend.security.validators import validate_question
from backend.security.uploads import save_uploaded_image
from backend.security.rate_limiter import (
    get_question_rate_limits,
)
from backend.services.mathematics import solve_mathematics
from backend.services.chemistry import solve_chemistry
from backend.services.physics import solve_physics
from backend.services.computer_science import solve_computer_science
from backend.services.ai_service import explain_with_ai


questions_bp = Blueprint("questions", __name__)


ENGINE_MAP = {
    "mathematics": solve_mathematics,
    "chemistry": solve_chemistry,
    "physics": solve_physics,
    "computer science": solve_computer_science,
}


@questions_bp.post("/solve")
@limiter.limit(get_question_rate_limits()[0])
def solve_question():
    subject = request.form.get("subject", "")
    question = request.form.get("question", "")

    valid, error = validate_question(subject, question)

    if not valid:
        return jsonify({
            "status": "error",
            "message": error,
        }), 400

    subject = subject.strip().lower()
    question = question.strip()

    engine = ENGINE_MAP[subject]
    engine_result = engine(question)

    if not isinstance(engine_result, dict):
        return jsonify({
            "status": "error",
            "message": "The solving engine returned an invalid response.",
        }), 500

    if engine_result.get("status") == "error":
        return jsonify(engine_result), 400

    if engine_result.get("status") in (
        "needs_information",
        "needs_ai",
    ):
        return jsonify(engine_result), 200

    ai_result = explain_with_ai(
        question,
        subject,
        engine_result,
    )

    if not isinstance(ai_result, dict):
        ai_result = {
            "status": "error",
            "explanation": None,
        }

    return jsonify({
        "status": "success",
        "subject": subject,
        "calculation": engine_result,
        "explanation": ai_result.get("explanation"),
        "ai_status": ai_result.get("status"),
    }), 200


@questions_bp.post("/upload-question")
@limiter.limit(get_question_rate_limits()[0])
def upload_question():
    if "photo" not in request.files:
        return jsonify({
            "status": "error",
            "message": "No image was uploaded.",
        }), 400

    photo = request.files["photo"]

    try:
        saved_path = save_uploaded_image(
            photo,
            current_app.config["UPLOAD_FOLDER"],
        )

        return jsonify({
            "status": "success",
            "message": "Image uploaded successfully.",
            "filename": Path(saved_path).name,
        }), 201

    except ValueError as error:
        return jsonify({
            "status": "error",
            "message": str(error),
        }), 400

    except OSError:
        current_app.logger.exception(
            "Failed to save uploaded question image."
        )
        return jsonify({
            "status": "error",
            "message": "Unable to save the uploaded image.",
        }), 500
