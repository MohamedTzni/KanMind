from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Owner can write, everyone can read.
    Supports different owner field names (owner/created_by/author).
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only to the owner/creator/author
        user = request.user

        if hasattr(obj, "owner"):
            return obj.owner == user
        if hasattr(obj, "created_by"):
            return obj.created_by == user
        if hasattr(obj, "author"):
            return obj.author == user

        return False


class IsOwnerOrMember(permissions.BasePermission):
    """
    Custom permission: Owner or members can access.
    Assumes obj has fields: owner and members (ManyToMany).
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if obj.owner == user:
            return True

        # members is expected to be a related manager (ManyToMany)
        return user in obj.members.all()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Read-only for everyone, write only for the owner/creator/author.
    This is commonly used in DRF and is expected by your tests.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only to the owner/creator/author
        user = request.user

        if hasattr(obj, "owner"):
            return obj.owner == user
        if hasattr(obj, "created_by"):
            return obj.created_by == user
        if hasattr(obj, "author"):
            return obj.author == user

        return False
