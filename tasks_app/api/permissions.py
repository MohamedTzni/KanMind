from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Allow write access only to the owner."""

    def get_owner(self, obj):
        for attr in ('owner', 'created_by', 'author'):
            try:
                return getattr(obj, attr)
            except AttributeError:
                pass
        return None

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return self.get_owner(obj) == request.user


class IsBoardMember(permissions.BasePermission):
    """Allow access only to members or owner of the task's board."""

    def has_object_permission(self, request, view, obj):
        board = obj.board
        if board.owner == request.user:
            return True
        return request.user in board.members.all()
