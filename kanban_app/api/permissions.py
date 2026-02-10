from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def get_owner(self, obj):
        for field in ['owner', 'created_by', 'author']:
            try:
                return getattr(obj, field)
            except AttributeError:
                continue
        return None

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return self.get_owner(obj) == request.user


class IsOwnerOrMember(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return request.user in obj.members.all()
