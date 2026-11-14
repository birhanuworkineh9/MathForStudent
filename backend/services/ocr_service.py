from PIL import Image, ImageOps, ImageEnhance
import pytesseract


def extract_question_text(image_path):
    try:
        image = Image.open(image_path).convert("RGB")

        image = ImageOps.grayscale(image)
        image = ImageEnhance.Contrast(image).enhance(1.5)

        text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )

        text = text.strip()

        if not text:
            return {
                "status": "needs_information",
                "message": "No readable text was found in the image."
            }

        return {
            "status": "success",
            "text": text
        }

    except Exception:
        return {
            "status": "error",
            "message": (
                "Image text recognition is unavailable. "
                "Check whether Tesseract OCR is installed."
            )
        }