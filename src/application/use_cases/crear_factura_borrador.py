"""Crea un borrador de factura."""

from __future__ import annotations

from decimal import Decimal

from src.domain.money import line_subtotal
from src.domain.tenancy import assert_same_empresa
from src.infrastructure.db.models import (
    Auditoria,
    Cliente,
    Factura,
    FacturaDetalle,
    Producto,
)


def crear_factura_borrador(
    *,
    empresa_id: int,
    sucursal_id: int,
    punto_venta_id: int,
    usuario_id: int,
    cliente_id: int,
    lineas: list[dict],
    actor_id: int | None = None,
) -> Factura:
    cliente = Cliente.objects.get(pk=cliente_id)
    assert_same_empresa(cliente.empresa_id, empresa_id)

    factura = Factura.objects.create(
        empresa_id=empresa_id,
        sucursal_id=sucursal_id,
        punto_venta_id=punto_venta_id,
        usuario_id=usuario_id,
        cliente_id=cliente_id,
        estado_interno=Factura.EstadoInterno.BORRADOR,
    )

    monto_total = Decimal("0")
    for linea in lineas:
        producto = Producto.objects.get(pk=linea["producto_id"])
        assert_same_empresa(producto.empresa_id, empresa_id)
        cantidad = Decimal(str(linea["cantidad"]))
        descuento = Decimal(str(linea.get("descuento", 0)))
        subtotal = line_subtotal(cantidad, producto.precio_unitario, descuento)
        FacturaDetalle.objects.create(
            factura=factura,
            actividad_economica=producto.actividad_economica,
            codigo_producto_sin=producto.codigo_producto_sin,
            codigo_producto=producto.codigo_interno,
            descripcion=producto.descripcion,
            cantidad=cantidad,
            unidad_medida=producto.unidad_medida,
            precio_unitario=producto.precio_unitario,
            descuento=descuento,
            subtotal=subtotal,
        )
        monto_total += subtotal

    factura.monto_total = monto_total
    factura.monto_total_sujeto_iva = monto_total
    factura.save(update_fields=["monto_total", "monto_total_sujeto_iva"])

    Auditoria.objects.create(
        empresa_id=empresa_id,
        actor_id=actor_id or usuario_id,
        accion="alta_factura",
        entidad="Factura",
        entidad_id=str(factura.pk),
        detalle={"estado": factura.estado_interno},
    )
    return factura


def cambiar_estado_factura(
    *, factura_id: int, empresa_id: int, nuevo_estado: str, actor_id: int
) -> Factura:
    factura = Factura.objects.get(pk=factura_id)
    assert_same_empresa(factura.empresa_id, empresa_id)
    anterior = factura.estado_interno
    factura.estado_interno = nuevo_estado
    factura.save(update_fields=["estado_interno", "updated_at"])
    Auditoria.objects.create(
        empresa_id=empresa_id,
        actor_id=actor_id,
        accion="cambio_estado_factura",
        entidad="Factura",
        entidad_id=str(factura.pk),
        detalle={"anterior": anterior, "nuevo": nuevo_estado},
    )
    return factura
