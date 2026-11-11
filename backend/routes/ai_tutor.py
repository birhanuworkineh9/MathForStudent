
from flask import Blueprint, request, jsonify, current_app

from ..services.ai_service import solve_with_ai


ai_tutor_bp = Blueprint(
    "ai_tutor",
    __name__,
    url_prefix="/api/ai-tutor"
)

ALLOWED_SUBJECTS = {
    "Mathematics",
    "Physics",
    "Chemistry",
    "Computer Science"
}


@ai_tutor_bp.route("/ask", methods=["POST"])
def ask_tutor():
    """Allow students to ask the AI tutor questions."""

    question = request.form.get(
        "question",
        ""
    ).strip()

    subject = request.form.get(
        "subject",
        ""
    ).strip()

    education_level = request.form.get(
        "education_level",
        "Grade 9"
    ).strip()

    image = request.files.get("image")

    if not question and not (
        image and image.filename
    ):
        return jsonify({
            "status": "error",
            "message": "Please enter a question or upload an image."
        }), 400

    if subject not in ALLOWED_SUBJECTS:
        return jsonify({
            "status": "error",
            "message": "Please select a valid subject."
        }), 400

    if image and image.filename:
        allowed_extensions = {
            "png", "jpg", "jpeg", "webp"
        }

        if (
            "." not in image.filename
            or image.filename.rsplit(".", 1)[1].lower()
            not in allowed_extensions
        ):
            return jsonify({
                "status": "error",
                "message": "Unsupported image format."
            }), 400

    try:
        answer = solve_with_ai(
            question=question,
            subject=subject,
            education_level=education_level,
            image=image if image and image.filename else None
        )

        return jsonify({
            "status": "success",
            "message": "AI tutor answered successfully.",
            "subject": subject,
            "answer": answer
        }), 200

    except RuntimeError as error:
        current_app.logger.error(
            "AI tutor configuration error: %s",
            error
        )

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 503

    except Exception:
        current_app.logger.exception(
            "AI tutor request failed."
        )

        return jsonify({
            "status": "error",
            "message": "The AI tutor could not answer. Please try again."
        }), 500
