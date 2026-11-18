from __future__ import annotations

import pytest

from src.application.use_cases.emitir_factura import emitir_factura
from src.application.use_cases.iniciar_contingencia import detectar_failover
from src.application.use_cases.obtener_cufd import obtener_cufd
from src.application.use_cases.regularizar_contingencia import regularizar_contingencia
from src.infrastructure.db.models import Factura
from src.infrastructure.siat.stub_client import StubSiatClient


@pytest.mark.django_db
def test_failover_a_offline(
    empresa_a, sucursal_a, pv_a, user_a, cliente_a, producto_a
):
    cufd = obtener_cufd(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        client=StubSiatClient(),
    )
    stub = StubSiatClient(comunicacion_ok=False)
    estado = detectar_failover(
        empresa_id=empresa_a.id, cufd_vigente=cufd.valor, client=stub
    )
    assert estado is not None
    assert estado.activa

    result = emitir_factura(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        usuario_id=user_a.id,
        cliente_id=cliente_a.id,
        lineas=[{"producto_id": producto_a.id, "cantidad": 1}],
        nit_emisor="1000001001",
        client=stub,
        forzar_offline=True,
    )
    assert result.offline is True
    assert result.factura.codigo_emision == 2
    assert result.factura.cufd == cufd.valor
    assert "recepcionFactura" not in stub.calls


@pytest.mark.django_db
def test_regularizacion_orden_cufd_evento_envio(
    empresa_a, sucursal_a, pv_a, user_a, cliente_a, producto_a
):
    cufd = obtener_cufd(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        client=StubSiatClient(),
    )
    stub = StubSiatClient(comunicacion_ok=False)
    estado = detectar_failover(
        empresa_id=empresa_a.id, cufd_vigente=cufd.valor, client=stub
    )
    assert estado and estado.evento

    for _ in range(3):
        emitir_factura(
            empresa_id=empresa_a.id,
            sucursal_id=sucursal_a.id,
            punto_venta_id=pv_a.id,
            usuario_id=user_a.id,
            cliente_id=cliente_a.id,
            lineas=[{"producto_id": producto_a.id, "cantidad": 1}],
            nit_emisor="1000001001",
            client=stub,
            forzar_offline=True,
        )

    # Recovery stub: communication back; status check returns not-yet-received
    stub.comunicacion_ok = True
    stub.estado_codigo = 0
    stub.paquete_recepcion_codigo = 901
    stub.paquete_validacion_codigo = 908

    result = regularizar_contingencia(
        empresa_id=empresa_a.id,
        evento_id=estado.evento.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        client=stub,
    )
    assert "solicitudCufd" in stub.calls
    assert result.evento.cufd_envio
    assert result.evento.fecha_fin
    assert len(result.paquetes) == 1
    assert result.paquetes[0].cantidad_facturas == 3
    assert result.paquetes[0].hash_sha256
    assert result.paquetes[0].estado_siat == "908"
    assert Factura.objects.filter(empresa=empresa_a, estado_siat="908").count() == 3


@pytest.mark.django_db
def test_no_duplicar_si_estado_ya_en_sin(
    empresa_a, sucursal_a, pv_a, user_a, cliente_a, producto_a
):
    cufd = obtener_cufd(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        client=StubSiatClient(),
    )
    stub = StubSiatClient(comunicacion_ok=False)
    estado = detectar_failover(
        empresa_id=empresa_a.id, cufd_vigente=cufd.valor, client=stub
    )
    emitir_factura(
        empresa_id=empresa_a.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        usuario_id=user_a.id,
        cliente_id=cliente_a.id,
        lineas=[{"producto_id": producto_a.id, "cantidad": 1}],
        nit_emisor="1000001001",
        client=stub,
        forzar_offline=True,
    )
    stub.comunicacion_ok = True
    stub.estado_codigo = 908  # already at SIN
    result = regularizar_contingencia(
        empresa_id=empresa_a.id,
        evento_id=estado.evento.id,
        sucursal_id=sucursal_a.id,
        punto_venta_id=pv_a.id,
        client=stub,
    )
    assert result.facturas_ya_en_sin
    assert result.paquetes == [] or all(p.cantidad_facturas == 0 for p in result.paquetes)
    assert "recepcionPaquete" not in stub.calls
