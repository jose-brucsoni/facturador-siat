from __future__ import annotations

import pytest

from src.application.use_cases.consultar_estado_factura import consultar_estado_factura
from src.application.use_cases.emitir_factura import emitir_factura
from src.application.use_cases.obtener_cufd import obtener_cufd
from src.infrastructure.siat.stub_client import StubSiatClient


@pytest.mark.django_db
def test_consulta_estado_por_cuf(
    empresa_a, sucursal_a, pv_a, user_a, cliente_a, producto_a
):
    obtener_cufd(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        client=StubSiatClient(),
    )
    stub = StubSiatClient()
    stub.emision_codigo = 908
    factura = emitir_factura(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        usuario_id=user_a.id,
        cliente_id=cliente_a.id,
        lineas=[{"producto_id": producto_a.id, "cantidad": 1}],
        nit_emisor="1000001001",
        client=stub,
    ).factura
    stub.estado_codigo = 908
    result = consultar_estado_factura(
        empresa_id=empresa_a.id, cuf=factura.cuf, client=stub
    )
    assert result["codigoEstado"] == "908"
    assert result["cuf"] == factura.cuf
