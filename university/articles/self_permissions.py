from rest_framework import permissions

class IsReviewerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                (request.user.is_reviewer or request.user.is_staff or request.user.is_superuser))

class IsStuffOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                (request.user.is_staff or request.user.is_superuser))


