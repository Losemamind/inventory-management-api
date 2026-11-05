
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):
    """
    อนุญาตเฉพาะ Admin
    """

    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and (
                user.is_superuser
                or user.role == 'admin'
            )
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Admin จัดการข้อมูลได้
    Staff ดูข้อมูลได้ และทำรายการรับเข้า/เบิกออกได้
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        if getattr(view, 'action', None) in ('stock_in', 'stock_out'):
            return True

        return (
            user.is_superuser
            or user.role == 'admin'
        )
