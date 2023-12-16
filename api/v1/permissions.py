# permissions.py
from rest_framework.permissions import BasePermission


class RiderOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            assert request.user.is_authenticated
            assert request.user.user_rider is not None
            return True
        except Exception:
            return False
