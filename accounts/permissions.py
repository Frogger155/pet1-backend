from rest_framework import permissions

class IsUserAccountOwnerOrAdmin(permissions.BasePermission):
    """
    Проверка, что пользователь, сделавший запрос к учетной записи,
    является ее владельцем.
    Если да, то дается разрешение на удаление.
    Если нет - то вызывать разрешается только SAFE-методы
    """
    def has_permission(self, request, view):

        return request.user.is_authenticated

    def has_object_permission(self, request, view, user_obj):
        if request.method in permissions.SAFE_METHODS:
            return True
                
        return request.user == user_obj or request.user.is_superuser