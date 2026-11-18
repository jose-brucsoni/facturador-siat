from __future__ import annotations

import pytest

from src.application.use_cases.emitir_factura import emitir_factura
from src.application.use_cases.generar_representacion_grafica import (
    generar_representacion_grafica,
)
from src.application.use_cases.listar_facturas import (
    listar_facturas,
    reenviar_factura_comprador,
)
from src.application.use_cases.obtener_cufd import obtener_cufd
from src.infrastructure.db.models import Auditoria
from src.infrastructure.notifications import ConsoleNotifier
from src.infrastructure.siat.stub_client import StubSiatClient


@pytest.mark.django_db
def test_historial_tenancy(
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
    from decimal import Decimal

    from src.infrastructure.db.models import Producto

    producto_b = Producto.objects.create(
        empresa=empresa_b,
        codigo_interno="P-B-1",
        descripcion="Producto B",
        actividad_economica="620100",
        codigo_producto_sin="83141",
        unidad_medida=58,
        precio_unitario=Decimal("50.00"),
    )
    for emp, suc, pv, user, cli, prod, nit in [
        (empresa_a, sucursal_a, pv_a, user_a, cliente_a, producto_a, empresa_a.nit),
        (empresa_b, sucursal_b, pv_b, user_b, cliente_b, producto_b, empresa_b.nit),
    ]:
        obtener_cufd(
            empresa_id=emp.id,
            sucursal_id=suc.id,
            punto_venta_id=pv.id,
            client=StubSiatClient(),
        )
        stub = StubSiatClient()
        stub.emision_codigo = 908
        emitir_factura(
            empresa_id=emp.id,
            sucursal_id=suc.id,
            punto_venta_id=pv.id,
            usuario_id=user.id,
            cliente_id=cli.id,
            lineas=[{"producto_id": prod.id, "cantidad": 1}],
            nit_emisor=nit,
            client=stub,
        )

    ids_a = set(listar_facturas(empresa_id=empresa_a.id).values_list("id", flat=True))
    ids_b = set(listar_facturas(empresa_id=empresa_b.id).values_list("id", flat=True))
    assert ids_a.isdisjoint(ids_b)
    assert len(ids_a) == 1
    assert len(ids_b) == 1


@pytest.mark.django_db
def test_reenvio_auditado(
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
        empresa_id=empresa_a.id, factura_id=factura.id
    )
    notifier = ConsoleNotifier()
    reenviar_factura_comprador(
        empresa_id=empresa_a.id,
        factura_id=factura.id,
        pdf_bytes=pdf,
        actor_id=user_a.id,
        notifier=notifier,
    )
    assert notifier.sent
    assert Auditoria.objects.filter(accion="reenvio_factura", entidad_id=str(factura.id)).exists()
