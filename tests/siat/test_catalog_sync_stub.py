"""Pruebas de sincronización de catálogos."""

from __future__ import annotations

import pytest

from src.application.use_cases.sincronizar_catalogos import sincronizar_catalogos
from src.infrastructure.db.models import CatalogoSiat
from src.infrastructure.siat.stub_client import StubSiatClient


@pytest.mark.django_db
def test_catalog_sync_upserts(empresa_a):
    stub = StubSiatClient()
    sincronizar_catalogos(empresa_id=empresa_a.id, client=stub)
    tipos = set(CatalogoSiat.objects.filter(empresa=empresa_a).values_list("tipo", flat=True))
    assert "leyendas" in tipos
    assert "tipo_factura" in tipos
    assert "metodo_pago" in tipos
    # Upsert again — no duplicates
    sincronizar_catalogos(empresa_id=empresa_a.id, client=stub)
    assert CatalogoSiat.objects.filter(empresa=empresa_a, tipo="tipo_factura").count() == 1
