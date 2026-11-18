from __future__ import annotations

from datetime import date, timedelta

import pytest

from src.application.use_cases.anular_factura import anular_factura
from src.application.use_cases.emitir_factura import emitir_factura
from src.application.use_cases.obtener_cufd import obtener_cufd
from src.domain.tenancy import TenantIsolationError
from src.infrastructure.db.models import Auditoria, Factura
from src.infrastructure.notifications import ConsoleNotifier
from src.infrastructure.siat.stub_client import StubSiatClient


@pytest.fixture
def factura_validada(empresa_a, sucursal_a, pv_a, user_a, cliente_a, producto_a):
    obtener_cufd(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        client=StubSiatClient(),
    )
    stub = StubSiatClient()
    stub.emision_codigo = 908
    return emitir_factura(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        usuario_id=user_a.id,
        cliente_id=cliente_a.id,
        lineas=[{"producto_id": producto_a.id, "cantidad": 1}],
        nit_emisor="1000001001",
        client=stub,
    ).factura


@pytest.mark.django_db
def test_anulacion_plazo_y_notificacion(factura_validada, empresa_a, user_a):
    stub = StubSiatClient()
    stub.anulacion_codigo = 905
    notifier = ConsoleNotifier()
    result = anular_factura(
        empresa_id=empresa_a.id,
        factura_id=factura_validada.id,
        motivo_codigo="1",
        motivo_descripcion="Error en datos",
        actor_id=user_a.id,
        client=stub,
        notifier=notifier,
    )
    assert result.fuera_de_plazo is False
    assert result.anulacion is not None
    assert result.anulacion.estado_siat == "905"
    factura_validada.refresh_from_db()
    assert factura_validada.estado_interno == Factura.EstadoInterno.ANULADA
    assert notifier.sent
    assert Auditoria.objects.filter(accion="anular_factura").exists()


@pytest.mark.django_db
def test_anulacion_fuera_de_plazo_no_llama_sin(factura_validada, empresa_a, user_a):
    stub = StubSiatClient()
    hoy = date.today() + timedelta(days=400)
    result = anular_factura(
        empresa_id=empresa_a.id,
        factura_id=factura_validada.id,
        motivo_codigo="1",
        actor_id=user_a.id,
        client=stub,
        hoy=hoy,
    )
    assert result.fuera_de_plazo is True
    assert "102600000025" in result.guia_rnd
    assert "anulacionFactura" not in stub.calls


@pytest.mark.django_db
def test_tenancy_en_emision(factura_validada, empresa_b, user_b):
    with pytest.raises(TenantIsolationError):
        anular_factura(
            empresa_id=empresa_b.id,
            factura_id=factura_validada.id,
            motivo_codigo="1",
            actor_id=user_b.id,
            client=StubSiatClient(),
        )
