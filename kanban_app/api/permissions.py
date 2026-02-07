from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission: Only the owner can update or delete
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.owner == request.user


class IsOwnerOrMember(permissions.BasePermission):
    """
    Custom permission: Owner or members can access
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if obj.owner == user:
            return True
        
        if user in obj.members.all():
            return True
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Owner can edit, others can only read
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.owner == request.user