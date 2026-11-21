
"""Question solving and image upload routes."""

from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from backend.extensions import limiter
from backend.security.rate_limiter import get_question_rate_limits
from backend.security.uploads import save_uploaded_image
from backend.security.validators import validate_question
from backend.services.ai_service import explain_with_ai
from backend.services.chemistry import solve_chemistry
from backend.services.computer_science import solve_computer_science
from backend.services.mathematics import solve_mathematics
from backend.services.ocr_service import extract_question_text
from backend.services.physics import solve_physics

questions_bp = Blueprint("questions", __name__)

ENGINE_MAP = {
    "mathematics": solve_mathematics,
    "chemistry": solve_chemistry,
    "physics": solve_physics,
    "computer science": solve_computer_science,
}


def _error(message, status_code=400):
    return jsonify({"status": "error", "message": message}), status_code


@questions_bp.post("/solve")
@limiter.limit(get_question_rate_limits()[0])
def solve_question():
    subject = request.form.get("subject", "").strip().lower()
    typed_question = request.form.get("question", "").strip()
    photo = request.files.get("photo")
    saved_path = None
    recognized_question = ""

    if subject not in ENGINE_MAP:
        return _error("Please select a valid subject.")

    try:
        if photo and photo.filename:
            saved_path = save_uploaded_image(
                photo, current_app.config["UPLOAD_FOLDER"]
            )
            ocr_result = extract_question_text(saved_path)

            if not isinstance(ocr_result, dict):
                return _error("Invalid OCR response.", 500)

            if ocr_result.get("status") != "success":
                status = ocr_result.get("status", "error")
                return jsonify({
                    "status": status,
                    "subject": subject,
                    "message": ocr_result.get(
                        "message", "Could not read the image."
                    ),
                }), 200 if status == "needs_information" else 400

            recognized_question = str(
                ocr_result.get("text", "")
            ).strip()

        question = "\n\n".join(
            part for part in (typed_question, recognized_question) if part
        )

        valid, error = validate_question(subject, question)
        if not valid:
            return _error(error or "Enter a question or upload a readable image.")

        engine_result = ENGINE_MAP[subject](question)

        if not isinstance(engine_result, dict):
            return _error("Invalid solving engine response.", 500)

        response_base = {
            "subject": subject,
            "recognized_question": recognized_question or None,
        }

        if engine_result.get("status") == "error":
            return jsonify({
                **response_base,
                **engine_result,
                "status": "error",
            }), 400

        if engine_result.get("status") in (
            "needs_information", "needs_ai"
        ):
            return jsonify({**response_base, **engine_result}), 200

        ai_result = explain_with_ai(question, subject, engine_result)
        if not isinstance(ai_result, dict):
            ai_result = {"status": "error", "explanation": None}

        return jsonify({
            "status": "success",
            **response_base,
            "calculation": engine_result,
            "explanation": ai_result.get("explanation"),
            "ai_status": ai_result.get("status"),
            "ai_message": ai_result.get("message"),
        }), 200

    except ValueError as error:
        return _error(str(error), 400)
    except OSError:
        current_app.logger.exception("Image processing failed.")
        return _error("Unable to process the uploaded image.", 500)
    except Exception:
        current_app.logger.exception("Unexpected solving error.")
        return _error("An unexpected error occurred.", 500)
    finally:
        if saved_path:
            try:
                Path(saved_path).unlink(missing_ok=True)
            except OSError:
                current_app.logger.warning(
                    "Could not remove temporary image: %s", saved_path
                )


@questions_bp.post("/upload-question")
@limiter.limit(get_question_rate_limits()[0])
def upload_question():
    if "photo" not in request.files:
        return _error("No image was uploaded.")

    saved_path = None
    try:
        saved_path = save_uploaded_image(
            request.files["photo"],
            current_app.config["UPLOAD_FOLDER"],
        )
        result = extract_question_text(saved_path)

        if not isinstance(result, dict):
            return _error("Invalid OCR response.", 500)

        if result.get("status") != "success":
            return jsonify(result), 400

        return jsonify({
            "status": "success",
            "message": "Question text recognized successfully.",
            "recognized_question": result.get("text", ""),
        }), 200

    except ValueError as error:
        return _error(str(error), 400)
    except OSError:
        current_app.logger.exception("Image processing failed.")
        return _error("Unable to process the uploaded image.", 500)
    finally:
        if saved_path:
            try:
                Path(saved_path).unlink(missing_ok=True)
            except OSError:
                current_app.logger.warning(
                    "Could not remove temporary image: %s", saved_path
                )
