from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only owners (authors) can edit/delete. Read access for others.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only for the author
        return obj.author == request.user
