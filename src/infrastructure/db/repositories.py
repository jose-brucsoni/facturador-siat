"""Consultas filtradas por empresa."""

from __future__ import annotations

from typing import TypeVar

from django.db import models

from src.domain.tenancy import TenantIsolationError, assert_same_empresa

from .models import Cliente, Factura, Producto

T = TypeVar("T", bound=models.Model)


def get_for_empresa(model: type[T], empresa_id: int, pk: int) -> T:
    try:
        obj = model.objects.get(pk=pk)
    except model.DoesNotExist as exc:
        raise TenantIsolationError("Recurso no encontrado.") from exc
    resource_empresa_id = getattr(obj, "empresa_id", None)
    if resource_empresa_id is None:
        raise TenantIsolationError("Recurso sin empresa.")
    assert_same_empresa(resource_empresa_id, empresa_id)
    return obj


def list_clientes(empresa_id: int):
    return Cliente.objects.filter(empresa_id=empresa_id)


def list_productos(empresa_id: int):
    return Producto.objects.filter(empresa_id=empresa_id)


def list_facturas(empresa_id: int):
    return Factura.objects.filter(empresa_id=empresa_id)
