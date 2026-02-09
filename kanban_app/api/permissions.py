from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            if obj.owner == request.user:
                return True
        except AttributeError:
            pass
        try:
            if obj.created_by == request.user:
                return True
        except AttributeError:
            pass
        try:
            if obj.author == request.user:
                return True
        except AttributeError:
            pass
        return False


class IsOwnerOrMember(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return request.user in obj.members.all()
