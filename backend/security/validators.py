
import re

VALID_SUBJECTS = {
    "mathematics",
    "physics",
    "chemistry",
    "computer science"
}


def validate_question(subject, question):
    if subject not in VALID_SUBJECTS:
        return False, "Invalid subject."

    if not question or not question.strip():
        return False, "Question is required."

    if len(question) > 15000:
        return False, "Question is too long."

    return True, None


def validate_registration(full_name, email, password):
    if not full_name or len(full_name.strip()) < 2:
        return False, "Enter your full name."

    if not email or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        email
    ):
        return False, "Enter a valid email address."

    if not password or len(password) < 10:
        return False, "Password must contain at least 10 characters."

    if len(password) > 128:
        return False, "Password is too long."

    return True, None
