
"""Password hashing and verification for MathForStudent."""

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)


MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128


def hash_password(password: str) -> str:
    """Securely hash a password using scrypt."""

    if not isinstance(password, str):
        raise ValueError("Password must be text.")

    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        raise ValueError(
            "Password must contain between 10 and 128 characters."
        )

    return generate_password_hash(
        password,
        method="scrypt",
    )


def verify_password(password_hash: str, password: str) -> bool:
    """Safely verify a password against its stored hash."""

    if not isinstance(password_hash, str):
        return False

    if not isinstance(password, str):
        return False

    if not password_hash or len(password) > MAX_PASSWORD_LENGTH:
        return False

    try:
        return check_password_hash(password_hash, password)
    except (ValueError, TypeError):
        return False
