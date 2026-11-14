from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from PIL import Image
import os

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
    "computer science": solve_computer_science
}


@questions_bp.post("/solve")
def solve_question():
    subject = request.form.get("subject", "").strip().lower()
    question = request.form.get("question", "").strip()

    if subject not in ENGINE_MAP:
        return jsonify({
            "status": "error",
            "message": "Select a valid subject."
        }), 400

    if not question:
        return jsonify({
            "status": "error",
            "message": "Enter your question."
        }), 400

    engine = ENGINE_MAP[subject]
    engine_result = engine(question)

    if engine_result.get("status") == "error":
        return jsonify(engine_result), 400

    if engine_result.get("status") in (
        "needs_information",
        "needs_ai"
    ):
        return jsonify(engine_result), 200

    ai_result = explain_with_ai(
        question,
        subject,
        engine_result
    )

    return jsonify({
        "status": "success",
        "subject": subject,
        "calculation": engine_result,
        "explanation": ai_result.get("explanation"),
        "ai_status": ai_result.get("status")
    }), 200


@questions_bp.post("/upload-question")
def upload_question():
    if "photo" not in request.files:
        return jsonify({
            "status": "error",
            "message": "No image was uploaded."
        }), 400

    photo = request.files["photo"]

    if not photo.filename:
        return jsonify({
            "status": "error",
            "message": "Select an image."
        }), 400

    extension = photo.filename.rsplit(".", 1)[-1].lower()

    if extension not in current_app.config["ALLOWED_EXTENSIONS"]:
        return jsonify({
            "status": "error",
            "message": "Unsupported image type."
        }), 400

    try:
        image = Image.open(photo.stream)
        image.verify()
        photo.stream.seek(0)

        filename = secure_filename(photo.filename)

        # Use a unique filename to avoid overwriting uploads.
        import uuid
        filename = f"{uuid.uuid4().hex}_{filename}"

        destination = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            filename
        )

        photo.save(destination)

        return jsonify({
            "status": "success",
            "message": "Image uploaded successfully.",
            "filename": filename
        }), 201

    except Exception:
        return jsonify({
            "status": "error",
            "message": "The uploaded file is not a valid image."
        }), 400
