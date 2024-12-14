from rest_framework import permissions

class IsLibrarian(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff

class IsOwnerOrLibrarian(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user