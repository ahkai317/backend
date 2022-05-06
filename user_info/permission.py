from rest_framework.permissions import BasePermission

class IsSelfOrReadOnly(BasePermission):
  def has_permission(self, request, view):
      return (request.user and request.user.is_authenticated)
  def has_object_permission(self, request, view, obj):
      if request.user.is_superuser:
        return True
      else:
        return obj == request.user