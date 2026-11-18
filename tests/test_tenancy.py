"""Pruebas de aislamiento entre empresas."""

from __future__ import annotations

import pytest

from src.application.use_cases.crear_factura_borrador import crear_factura_borrador
from src.domain.tenancy import TenantIsolationError
from src.infrastructure.db.models import Factura
from src.infrastructure.db.repositories import get_for_empresa, list_clientes, list_facturas


def test_empresa_a_no_ve_clientes_de_b(empresa_a, empresa_b, cliente_a, cliente_b):
    ids = set(list_clientes(empresa_a.id).values_list("id", flat=True))
    assert cliente_a.id in ids
    assert cliente_b.id not in ids


def test_empresa_a_no_lee_cliente_de_b(empresa_a, cliente_b):
    with pytest.raises(TenantIsolationError):
        get_for_empresa(cliente_b.__class__, empresa_a.id, cliente_b.id)


def test_empresa_a_no_ve_facturas_de_b(
    empresa_a,
    empresa_b,
    sucursal_a,
    sucursal_b,
    pv_a,
    pv_b,
    user_a,
    user_b,
    cliente_a,
    cliente_b,
    producto_a,
):
    from src.infrastructure.db.models import Producto
    from decimal import Decimal

    producto_b = Producto.objects.create(
        empresa=empresa_b,
        codigo_interno="P-B-1",
        descripcion="Producto B",
        actividad_economica="620100",
        codigo_producto_sin="83141",
        unidad_medida=58,
        precio_unitario=Decimal("50.00"),
    )
    fa = crear_factura_borrador(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        usuario_id=user_a.id,
        cliente_id=cliente_a.id,
        lineas=[{"producto_id": producto_a.id, "cantidad": 1}],
    )
    fb = crear_factura_borrador(
        empresa_id=empresa_b.id,
        sucursal_id=sucursal_b.id,
        punto_venta_id=pv_b.id,
        usuario_id=user_b.id,
        cliente_id=cliente_b.id,
        lineas=[{"producto_id": producto_b.id, "cantidad": 1}],
    )
    ids = set(list_facturas(empresa_a.id).values_list("id", flat=True))
    assert fa.id in ids
    assert fb.id not in ids

    with pytest.raises(TenantIsolationError):
        get_for_empresa(Factura, empresa_a.id, fb.id)
