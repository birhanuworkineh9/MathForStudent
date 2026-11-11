
"""
MathForStudent Upload Security

Validates uploaded question images and stores them safely.
"""

import os
import uuid

from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


def allowed_image(filename: str) -> bool:
    """Check whether an image extension is allowed."""

    if not isinstance(filename, str) or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


def save_uploaded_image(image, upload_folder: str):
    """
    Validate and safely save an uploaded image.

    Returns the saved file path.
    Raises ValueError when the upload is invalid.
    """

    if image is None or not image.filename:
        raise ValueError("No image was provided.")

    if not allowed_image(image.filename):
        raise ValueError("Unsupported image format.")

    image.seek(0, os.SEEK_END)
    file_size = image.tell()
    image.seek(0)

    if file_size == 0:
        raise ValueError("The uploaded image is empty.")

    if file_size > MAX_IMAGE_SIZE:
        raise ValueError("Image must not exceed 5 MB.")

    os.makedirs(upload_folder, exist_ok=True)

    original_name = secure_filename(image.filename)

    if not original_name:
        raise ValueError("Invalid image filename.")

    extension = original_name.rsplit(".", 1)[1].lower()

    filename = f"{uuid.uuid4().hex}.{extension}"

    file_path = os.path.join(
        upload_folder,
        filename
    )

    image.save(file_path)

    return file_path
