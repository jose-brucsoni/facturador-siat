from __future__ import annotations

from rest_framework.permissions import BasePermission


class HasEmpresa(BasePermission):
    message = "El usuario no tiene empresa asignada."

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "empresa_id", None)
        )
