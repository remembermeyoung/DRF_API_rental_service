from rest_framework import permissions


class BicycleDetailPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_authenticated)


class NotAuthorisedPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_authenticated
