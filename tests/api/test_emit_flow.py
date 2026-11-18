from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from src.application.use_cases.obtener_cufd import obtener_cufd
from src.infrastructure.siat.stub_client import StubSiatClient


@pytest.mark.django_db
def test_api_emision_stub(
    empresa_a, sucursal_a, pv_a, user_a, cliente_a, producto_a
):
    obtener_cufd(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        client=StubSiatClient(),
    )
    c = APIClient()
    c.force_authenticate(user=user_a)
    r = c.post(
        "/api/v1/emitir/",
        data={
            "cliente_id": cliente_a.id,
            "sucursal_id": sucursal_a.id,
            "punto_venta_id": pv_a.id,
            "lineas": [{"producto_id": producto_a.id, "cantidad": 1}],
        },
        format="json",
    )
    assert r.status_code == 201, r.content
    payload = r.json()
    assert payload["estado_siat"] == "908"
    assert payload["cuf"]
    assert payload["pdf_url"]

    pdf = c.get(payload["pdf_url"])
    assert pdf.status_code == 200
    assert pdf["Content-Type"] == "application/pdf"

    hist = c.get("/api/v1/facturas/")
    assert hist.status_code == 200
    assert any(row["id"] == payload["id"] for row in hist.json())
