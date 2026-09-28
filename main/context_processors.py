from main.permissions import can_create_or_delete, can_edit, role_label


def user_role(request):
    user = request.user
    return {
        "user_role": role_label(user),
        "can_edit": can_edit(user),
        "can_create_or_delete": can_create_or_delete(user),
    }