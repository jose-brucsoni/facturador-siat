from __future__ import annotations

import pytest

from src.application.use_cases.emitir_factura import emitir_factura
from src.application.use_cases.generar_representacion_grafica import (
    generar_representacion_grafica,
)
from src.application.use_cases.obtener_cufd import obtener_cufd
from src.infrastructure.pdf.qr import build_qr_url
from src.infrastructure.siat.stub_client import StubSiatClient


def test_qr_url_piloto():
    url = build_qr_url(
        nit="1000001001",
        cuf="ABC123",
        numero=7,
        tamano=2,
        base_url="https://pilotosiat.impuestos.gob.bo/consulta/QR",
    )
    assert url.startswith("https://pilotosiat.impuestos.gob.bo/consulta/QR?")
    assert "nit=1000001001" in url
    assert "cuf=ABC123" in url
    assert "numero=7" in url
    assert "t=2" in url


@pytest.mark.django_db
def test_pdf_contiene_campos_minimos(
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
        nit_emisor=empresa_a.nit,
        client=stub,
    ).factura
    pdf = generar_representacion_grafica(
        empresa_id=empresa_a.id, factura_id=factura.id, actor_id=user_a.id
    )
    assert pdf.startswith(b"%PDF")
    # Extract text streams loosely
    text = pdf.decode("latin-1", errors="ignore")
    assert empresa_a.nit in text
    assert str(factura.numero_factura) in text
    assert "CUF" in text
    assert str(factura.monto_total) in text or "Monto Total" in text
