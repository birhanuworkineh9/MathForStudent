
"""Permission and role checks for MathForStudent."""

from flask_login import current_user


# Roles supported by the application.
ROLE_STUDENT = "student"
ROLE_ADMIN = "admin"


def is_authenticated() -> bool:
    """Return True when a user is logged in."""
    return bool(current_user.is_authenticated)


def has_role(role: str) -> bool:
    """Check a user's role safely.

    The current User model does not yet define a role field.
    Until that field is added, users have no admin privileges.
    """
    if not is_authenticated() or not isinstance(role, str):
        return False

    user_role = getattr(current_user, "role", ROLE_STUDENT)
    return user_role == role.strip().lower()


def is_student() -> bool:
    """Check whether the current user is a student."""
    return has_role(ROLE_STUDENT)


def is_admin() -> bool:
    """Check whether the current user is an administrator."""
    return has_role(ROLE_ADMIN)


def can_access_user_data(user_id: int) -> bool:
    """Allow users to access only their own data.

    Administrators may access data only after an explicit role
    field and administrator management system are implemented.
    """
    if not is_authenticated():
        return False

    try:
        requested_user_id = int(user_id)
    except (TypeError, ValueError):
        return False

    return current_user.id == requested_user_id
