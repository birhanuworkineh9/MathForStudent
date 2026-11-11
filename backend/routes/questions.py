 
import os

from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Question
from ..services.ai_service import solve_with_ai


questions_bp = Blueprint(
    "questions",
    __name__,
    url_prefix="/api/questions"
)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

ALLOWED_SUBJECTS = {
    "Mathematics",
    "Physics",
    "Chemistry",
    "Computer Science"
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@questions_bp.route("/solve", methods=["POST"])
def solve_question():
    """Solve a typed or uploaded student question."""

    question_text = request.form.get(
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

    if subject not in ALLOWED_SUBJECTS:
        return jsonify({
            "status": "error",
            "message": "Please select a valid subject."
        }), 400

    if not question_text and (
        image is None or not image.filename
    ):
        return jsonify({
            "status": "error",
            "message": "Enter a question or upload an image."
        }), 400

    image_path = None

    if image and image.filename:
        if not allowed_file(image.filename):
            return jsonify({
                "status": "error",
                "message": "Unsupported image format."
            }), 400

        filename = secure_filename(image.filename)

        upload_folder = current_app.config.get(
            "UPLOAD_FOLDER",
            os.path.join(
                current_app.instance_path,
                "uploads"
            )
        )

        os.makedirs(upload_folder, exist_ok=True)

        image_path = os.path.join(
            upload_folder,
            filename
        )

        image.save(image_path)

        # Reopen the saved image for the AI service.
        image.stream = open(image_path, "rb")

    try:
        answer = solve_with_ai(
            question=question_text,
            subject=subject,
            education_level=education_level,
            image=image
        )

        user_id = (
            current_user.id
            if current_user.is_authenticated
            else None
        )

        question_record = Question(
            user_id=user_id,
            subject=subject,
            question_text=question_text or "Uploaded image question",
            image_path=image_path,
            answer=answer,
            explanation=answer
        )

        db.session.add(question_record)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Question solved successfully.",
            "question_id": question_record.id,
            "subject": subject,
            "answer": answer
        }), 200

    except Exception:
        db.session.rollback()

        current_app.logger.exception(
            "Question solving failed."
        )

        return jsonify({
            "status": "error",
            "message": "Unable to solve the question. Please try again."
        }), 500

    finally:
        if image and not image.stream.closed:
            image.stream.close()
       
