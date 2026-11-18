from __future__ import annotations

import pytest

from src.application.use_cases.emitir_factura import emitir_factura
from src.application.use_cases.obtener_cufd import obtener_cufd
from src.infrastructure.db.models import Factura, FacturaEvidencia
from src.infrastructure.siat.stub_client import StubSiatClient


@pytest.fixture
def cufd_a(empresa_a, sucursal_a, pv_a):
    return obtener_cufd(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        client=StubSiatClient(),
    )


@pytest.mark.django_db
def test_emision_908_guarda_evidencias(
    empresa_a, sucursal_a, pv_a, user_a, cliente_a, producto_a, cufd_a
):
    stub = StubSiatClient()
    stub.emision_codigo = 908
    result = emitir_factura(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        usuario_id=user_a.id,
        cliente_id=cliente_a.id,
        lineas=[{"producto_id": producto_a.id, "cantidad": 1}],
        nit_emisor="1000001001",
        client=stub,
        sync=True,
    )
    f = result.factura
    assert f.estado_interno == Factura.EstadoInterno.VALIDADA
    assert f.estado_siat == "908"
    assert f.codigo_recepcion
    assert FacturaEvidencia.objects.filter(factura=f, tipo="xml_emision").exists()
    assert FacturaEvidencia.objects.filter(factura=f, tipo="recepcion").exists()
    assert f.cuf


@pytest.mark.django_db
def test_emision_904_no_queda_valida(
    empresa_a, sucursal_a, pv_a, user_a, cliente_a, producto_a, cufd_a
):
    stub = StubSiatClient()
    stub.emision_codigo = 904
    result = emitir_factura(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        usuario_id=user_a.id,
        cliente_id=cliente_a.id,
        lineas=[{"producto_id": producto_a.id, "cantidad": 1}],
        nit_emisor="1000001001",
        client=stub,
        sync=True,
    )
    f = result.factura
    assert f.estado_interno == Factura.EstadoInterno.OBSERVADA
    assert f.estado_siat == "904"
    assert f.errores_siat
