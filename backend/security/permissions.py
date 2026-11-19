
"""Permission and role checks for MathForStudent."""

from flask_login import current_user


ROLE_STUDENT = "student"
ROLE_ADMIN = "admin"


def is_authenticated() -> bool:
    """Check whether a user is logged in."""
    return bool(current_user.is_authenticated)


def get_current_role() -> str | None:
    """Return the current user's role, if authenticated."""

    if not is_authenticated():
        return None

    role = getattr(current_user, "role", ROLE_STUDENT)

    if not isinstance(role, str):
        return ROLE_STUDENT

    return role.strip().lower()


def has_role(role: str) -> bool:
    """Check whether the current user has the requested role."""

    if not isinstance(role, str) or not role.strip():
        return False

    return get_current_role() == role.strip().lower()


def is_student() -> bool:
    """Check whether the current user is a student."""
    return has_role(ROLE_STUDENT)


def is_admin() -> bool:
    """Check whether the current user is an administrator."""
    return has_role(ROLE_ADMIN)


def can_access_user_data(user_id: int) -> bool:
    """Allow users to access only their own data."""

    if not is_authenticated():
        return False

    try:
        requested_user_id = int(user_id)
        current_user_id = int(current_user.id)
    except (TypeError, ValueError):
        return False

    return current_user_id == requested_user_id
