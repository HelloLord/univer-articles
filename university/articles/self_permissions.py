from rest_framework import permissions

class IsReviewerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Проверяем, что пользователь аутентифицирован и является ревьюером или администратором
        return (request.user.is_authenticated and
                (request.user.reviewer or request.user.is_staff or request.user.is_superuser))