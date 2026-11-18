"""Aislamiento entre empresas."""

from __future__ import annotations


class TenantIsolationError(Exception):
    """Intento de usar datos de otra empresa."""

    def __init__(self, message: str = "Acceso denegado: recurso de otra empresa.") -> None:
        super().__init__(message)


def assert_same_empresa(resource_empresa_id: int, actor_empresa_id: int) -> None:
    if resource_empresa_id != actor_empresa_id:
        raise TenantIsolationError()
