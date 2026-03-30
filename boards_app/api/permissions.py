from rest_framework import permissions


class IsOwnerOrMember(permissions.BasePermission):
    """Allow access only to the board owner or a board member."""

    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user
        is_member = obj.members.filter(id=request.user.id).exists()
        return is_owner or is_member