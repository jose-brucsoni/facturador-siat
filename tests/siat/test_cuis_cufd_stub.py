"""Pruebas de CUIS y CUFD en modo demo."""

from __future__ import annotations

import pytest

from src.application.use_cases.obtener_cufd import obtener_cufd
from src.application.use_cases.obtener_cuis import obtener_cuis
from src.infrastructure.db.models import CodigoOperacion, FacturaEvidencia
from src.infrastructure.siat.stub_client import StubSiatClient


@pytest.mark.django_db
def test_cuis_cufd_stub_persists(empresa_a, sucursal_a, pv_a):
    stub = StubSiatClient()
    cuis = obtener_cuis(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        client=stub,
    )
    cufd = obtener_cufd(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        cuis=cuis.valor,
        client=stub,
    )
    assert cuis.tipo == CodigoOperacion.Tipo.CUIS
    assert cuis.valor.startswith("STUB-CUIS")
    assert cufd.tipo == CodigoOperacion.Tipo.CUFD
    assert cufd.codigo_control
    assert FacturaEvidencia.objects.filter(empresa=empresa_a, tipo="cuis").exists()
    assert FacturaEvidencia.objects.filter(empresa=empresa_a, tipo="cufd").exists()
    assert cuis.raw_request and cuis.raw_response
