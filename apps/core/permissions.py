from rest_framework.permissions import BasePermission


class IsModeratorOrAdmin(BasePermission):
    message = "Moderator access is required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in {"moderator", "admin"}
        )

