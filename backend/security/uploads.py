
"""Secure image upload utilities for MathForStudent."""

import os
import uuid
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
}

ALLOWED_IMAGE_FORMATS = {
    "PNG": {"png"},
    "JPEG": {"jpg", "jpeg"},
    "WEBP": {"webp"},
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


def allowed_image(filename: str) -> bool:
    """Check whether the filename has an allowed extension."""

    if not isinstance(filename, str) or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def validate_image(image) -> str:
    """Validate image size, extension, and actual image format.

    Returns the validated extension.
    Raises ValueError if the image is invalid.
    """

    if image is None or not getattr(image, "filename", None):
        raise ValueError("No image was provided.")

    original_name = secure_filename(image.filename)

    if not original_name or not allowed_image(original_name):
        raise ValueError("Unsupported image format.")

    extension = original_name.rsplit(".", 1)[1].lower()

    try:
        image.stream.seek(0, os.SEEK_END)
        file_size = image.stream.tell()
        image.stream.seek(0)

        if file_size == 0:
            raise ValueError("The uploaded image is empty.")

        if file_size > MAX_IMAGE_SIZE:
            raise ValueError("Image must not exceed 5 MB.")

        with Image.open(image.stream) as picture:
            image_format = picture.format

            if image_format not in ALLOWED_IMAGE_FORMATS:
                raise ValueError("Unsupported image content.")

            if extension not in ALLOWED_IMAGE_FORMATS[image_format]:
                raise ValueError(
                    "Image extension does not match its content."
                )

            picture.verify()

        image.stream.seek(0)
        return extension

    except ValueError:
        image.stream.seek(0)
        raise

    except (UnidentifiedImageError, OSError) as error:
        image.stream.seek(0)
        raise ValueError(
            "The uploaded file is not a valid image."
        ) from error


def save_uploaded_image(image, upload_folder: str) -> str:
    """Validate and safely save an uploaded image.

    Returns the saved file path.
    Raises ValueError when the upload is invalid.
    """

    extension = validate_image(image)

    if not isinstance(upload_folder, (str, os.PathLike)):
        raise ValueError("Invalid upload folder.")

    folder = Path(upload_folder)
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{extension}"
    file_path = folder / filename

    try:
        image.stream.seek(0)

        with file_path.open("xb") as destination:
            while True:
                chunk = image.stream.read(64 * 1024)

                if not chunk:
                    break

                destination.write(chunk)

        return str(file_path)

    except OSError:
        file_path.unlink(missing_ok=True)
        raise
    finally:
        image.stream.seek(0)



    