
"""Input validation utilities for MathForStudent."""

import re


VALID_SUBJECTS = {
    "mathematics",
    "physics",
    "chemistry",
    "computer science",
}

MAX_QUESTION_LENGTH = 15000
MAX_NAME_LENGTH = 120
MAX_EMAIL_LENGTH = 254
MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128


def validate_question(subject, question):
    """Validate a question's subject and text."""

    if not isinstance(subject, str):
        return False, "Invalid subject."

    if subject.strip().lower() not in VALID_SUBJECTS:
        return False, "Invalid subject."

    if not isinstance(question, str) or not question.strip():
        return False, "Question is required."

    if len(question.strip()) > MAX_QUESTION_LENGTH:
        return False, "Question is too long."

    return True, None


def validate_registration(full_name, email, password):
    """Validate registration details."""

    if not isinstance(full_name, str):
        return False, "Enter your full name."

    full_name = full_name.strip()

    if len(full_name) < 2:
        return False, "Full name must contain at least 2 characters."

    if len(full_name) > MAX_NAME_LENGTH:
        return False, "Full name is too long."

    if not isinstance(email, str):
        return False, "Enter a valid email address."

    email = email.strip()

    if len(email) > MAX_EMAIL_LENGTH:
        return False, "Email address is too long."

    if not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        email,
    ):
        return False, "Enter a valid email address."

    if not isinstance(password, str):
        return False, "Password must be text."

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, (
            "Password must contain at least 10 characters."
        )

    if len(password) > MAX_PASSWORD_LENGTH:
        return False, "Password is too long."

    return True, None
