"""
MathForStudent Password Security

Provides secure password hashing and verification.
"""

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


def hash_password(password: str) -> str:
    """Securely hash a student's password."""

    if not isinstance(password, str):
        raise ValueError("Password must be text.")

    if len(password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    return generate_password_hash(
        password,
        method="scrypt"
    )


def verify_password(password_hash: str, password: str) -> bool:
    """Verify a password against its stored hash."""

    if not isinstance(password_hash, str):
        return False

    if not isinstance(password, str):
        return False

    try:
        return check_password_hash(
            password_hash,
            password
        )
    except (ValueError, TypeError):
        return False

