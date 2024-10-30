from rest_framework import permissions

class IsPostAuthorOrAdmin(permissions.BasePermission):
    """
    Проверка, является ли пользователь, сделавший запрос,
    автором поста. Если да, то разрешается делать любой тип запроса.
    Если нет, то разрешаются только SAFE-методы.

    Если пользователь является суперпользователем, то разрешается любой запрос
    """
    
    def has_permission(self, request, view):
        return True
    def has_object_permission(self, request, view, obj):
        return request.user == obj.author or request.user.is_superuser
    