from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Allow write access only to the owner."""

    def get_owner(self, obj):
        """Return the owner of the object."""
        try:
            return obj.owner
        except AttributeError:
            pass
        try:
            return obj.created_by
        except AttributeError:
            pass
        try:
            return obj.author
        except AttributeError:
            pass
        return None

    def has_object_permission(self, request, view, obj):
        """Allow read for everyone, write only for owner."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return self.get_owner(obj) == request.user


class IsOwnerOrMember(permissions.BasePermission):
    """Allow read access to owner and members, write access only to owner."""

    def has_object_permission(self, request, view, obj):
        """
        Check if user is board owner or member.
        Provides both read and write access to owners and members of the board.
        """
        is_owner = obj.owner == request.user
        is_member = obj.members.filter(id=request.user.id).exists()

        return is_owner or is_member


class IsBoardMember(permissions.BasePermission):
    """Allow access only to members or owner of the task's board."""

    def has_object_permission(self, request, view, obj):
        """Check if user is owner or member of the task's board."""
        board = obj.board
        if board.owner == request.user:
            return True
        return request.user in board.members.all()
