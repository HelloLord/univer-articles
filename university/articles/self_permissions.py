from rest_framework import permissions

# Проверяем, что пользователь аутентифицирован и является ревьюером или администратором
class IsReviewerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                (request.user.reviewer or request.user.is_staff or request.user.is_superuser))

# Проверяем, что пользователь аутентифицирован и является модератором или администратором
class IsStuffOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                (request.user.is_staff or request.user.is_superuser))


