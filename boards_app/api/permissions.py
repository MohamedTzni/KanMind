from rest_framework import permissions


class IsOwnerOrMember(permissions.BasePermission):
    """Allow access to board owners and members."""

    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user
        is_member = obj.members.filter(id=request.user.id).exists()
        return is_owner or is_member
