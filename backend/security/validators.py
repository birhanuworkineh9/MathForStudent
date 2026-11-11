
"""
MathForStudent Input Validation

Validates student registration and question inputs.
"""

import re


ALLOWED_SUBJECTS = {
    "Mathematics",
    "Physics",
    "Chemistry",
    "Computer Science"
}


def validate_email(email: str) -> bool:
    """Check whether an email address has a valid format."""

    if not isinstance(email, str):
        return False

    email = email.strip()

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return bool(re.fullmatch(pattern, email))


def validate_full_name(full_name: str) -> bool:
    """Validate a student's full name."""

    if not isinstance(full_name, str):
        return False

    full_name = full_name.strip()

    return 2 <= len(full_name) <= 120


def validate_password(password: str) -> bool:
    """Check minimum password requirements."""

    return (
        isinstance(password, str)
        and len(password) >= 8
        and len(password) <= 128
    )


def validate_subject(subject: str) -> bool:
    """Check whether the selected subject is supported."""

    return subject in ALLOWED_SUBJECTS


def validate_question(question: str) -> bool:
    """Check whether question text is acceptable."""

    return (
        isinstance(question, str)
        and 1 <= len(question.strip()) <= 20000
  )
  
