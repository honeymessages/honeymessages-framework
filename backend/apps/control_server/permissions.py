from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of an object.
        if hasattr(obj, "owner"):
            return request.user and obj.owner == request.user

        if hasattr(obj, "creator"):
            return request.user and obj.creator == request.user

        # objects without owner or creator can be modified by everybody
        return True
