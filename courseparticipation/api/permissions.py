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
    Custom permission to only allow authenticated users or admins to create an object for the given user.
    """
    def has_permission(self, request, view):
        # If requesting user is an admin, view and creation permissions are conceded
        if(request.user.is_staff):
            return True
        # If a user_id is given by a non-admin user as an argument in the request,
        # it needs to be the user's own ID
        if ('user_id' in request.data):
            if(int(request.data['user_id']) == request.user.id):
                return True
            else:
                return False
        # If no user_id given in request, the retrieval of the user will be handled in views.py
        return True

        
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # TODO: ensure that permissions allow only the user that created this participation (and the admin),
        # but not other users to delete a participation
        if (obj.user_id == request.user.id or request.user.is_staff):
            return True
        else:
            return False