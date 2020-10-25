from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit an object, and all others to view it.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
            return True

        # Write permissions are only allowed to admins.
        return request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """

    """
    # Read permissions are allowed to any authenticated request,
    # so we'll always allow GET, HEAD or OPTIONS requests.
    if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
        return True
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        # (Read and write) permissions are only allowed to admins and the owner of the participation.
        if (obj.participation_user_id == request.user or request.user.is_staff):
            return True
        else:
            return False