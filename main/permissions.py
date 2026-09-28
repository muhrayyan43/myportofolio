from django.core.exceptions import PermissionDenied

# The group name must match the group created in Django Admin.
EDITOR_GROUP_NAME = "Editor"


def is_owner(user):
    """True for the portfolio owner (the superuser)."""
    return user.is_authenticated and user.is_superuser


def is_editor(user):
    return (
        user.is_authenticated
        and user.groups.filter(name=EDITOR_GROUP_NAME).exists()
    )


def can_edit(user):
    """May update existing data: owners and editors."""
    return is_owner(user) or is_editor(user)


def can_create_or_delete(user):
    """May create or delete data: owners only."""
    return is_owner(user)


def role_label(user):
    """Human-readable role name, used for the navbar badge."""
    if not user.is_authenticated:
        return "Visitor"
    if is_owner(user):
        return "Owner"
    if is_editor(user):
        return "Editor"
    return "Member"


def require_can_edit(user):
    """Raise HTTP 403 unless the user may update data."""
    if not can_edit(user):
        raise PermissionDenied


def require_owner(user):
    """Raise HTTP 403 unless the user is the portfolio owner."""
    if not is_owner(user):
        raise PermissionDenied