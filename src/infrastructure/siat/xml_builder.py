"""Arma el XML de una factura Compra-Venta."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence
from xml.sax.saxutils import escape


@dataclass
class DetalleXml:
    actividad_economica: str
    codigo_producto_sin: str
    codigo_producto: str
    descripcion: str
    cantidad: Decimal
    unidad_medida: int
    precio_unitario: Decimal
    descuento: Decimal
    subtotal: Decimal


@dataclass
class FacturaXmlInput:
    nit_emisor: str
    razon_social_emisor: str
    municipio: str
    telefono: str
    numero_factura: int
    cuf: str
    cufd: str
    codigo_sucursal: int
    direccion: str
    codigo_punto_venta: int
    fecha_emision: str  # e.g. 2020-02-15T08:40:12.215
    nombre_razon_social: str
    codigo_tipo_documento_identidad: int
    numero_documento: str
    complemento: str
    codigo_cliente: str
    codigo_metodo_pago: int
    monto_total: Decimal
    monto_total_sujeto_iva: Decimal
    codigo_moneda: int
    tipo_cambio: Decimal
    monto_total_moneda: Decimal
    leyenda: str
    usuario: str
    codigo_documento_sector: int = 1
    codigo_emision: int = 1
    tipo_factura_documento: int = 1
    codigo_excepcion: int = 0
    descuento_adicional: Decimal = Decimal("0")
    detalles: Sequence[DetalleXml] = ()


def _d(value: Decimal) -> str:
    return f"{value:.2f}"


def build_compra_venta_xml(data: FacturaXmlInput) -> bytes:
    """Devuelve el XML de la factura."""
    detalles_xml = []
    for d in data.detalles:
        detalles_xml.append(
            f"""    <detalle>
      <actividadEconomica>{escape(d.actividad_economica)}</actividadEconomica>
      <codigoProductoSin>{escape(d.codigo_producto_sin)}</codigoProductoSin>
      <codigoProducto>{escape(d.codigo_producto)}</codigoProducto>
      <descripcion>{escape(d.descripcion)}</descripcion>
      <cantidad>{d.cantidad}</cantidad>
      <unidadMedida>{d.unidad_medida}</unidadMedida>
      <precioUnitario>{d.precio_unitario}</precioUnitario>
      <montoDescuento>{d.descuento}</montoDescuento>
      <subTotal>{d.subtotal}</subTotal>
    </detalle>"""
        )
    complemento = (
        f"    <complemento>{escape(data.complemento)}</complemento>\n"
        if data.complemento
        else ""
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<facturaComputarizadaCompraVenta>
  <cabecera>
    <nitEmisor>{escape(data.nit_emisor)}</nitEmisor>
    <razonSocialEmisor>{escape(data.razon_social_emisor)}</razonSocialEmisor>
    <municipio>{escape(data.municipio)}</municipio>
    <telefono>{escape(data.telefono)}</telefono>
    <numeroFactura>{data.numero_factura}</numeroFactura>
    <cuf>{escape(data.cuf)}</cuf>
    <cufd>{escape(data.cufd)}</cufd>
    <codigoSucursal>{data.codigo_sucursal}</codigoSucursal>
    <direccion>{escape(data.direccion)}</direccion>
    <codigoPuntoVenta>{data.codigo_punto_venta}</codigoPuntoVenta>
    <fechaEmision>{escape(data.fecha_emision)}</fechaEmision>
    <nombreRazonSocial>{escape(data.nombre_razon_social)}</nombreRazonSocial>
    <codigoTipoDocumentoIdentidad>{data.codigo_tipo_documento_identidad}</codigoTipoDocumentoIdentidad>
    <numeroDocumento>{escape(data.numero_documento)}</numeroDocumento>
{complemento}    <codigoCliente>{escape(data.codigo_cliente)}</codigoCliente>
    <codigoMetodoPago>{data.codigo_metodo_pago}</codigoMetodoPago>
    <montoTotal>{_d(data.monto_total)}</montoTotal>
    <montoTotalSujetoIva>{_d(data.monto_total_sujeto_iva)}</montoTotalSujetoIva>
    <codigoMoneda>{data.codigo_moneda}</codigoMoneda>
    <tipoCambio>{data.tipo_cambio}</tipoCambio>
    <montoTotalMoneda>{_d(data.monto_total_moneda)}</montoTotalMoneda>
    <descuentoAdicional>{_d(data.descuento_adicional)}</descuentoAdicional>
    <codigoExcepcion>{data.codigo_excepcion}</codigoExcepcion>
    <leyenda>{escape(data.leyenda)}</leyenda>
    <usuario>{escape(data.usuario)}</usuario>
    <codigoDocumentoSector>{data.codigo_documento_sector}</codigoDocumentoSector>
  </cabecera>
{chr(10).join(detalles_xml)}
</facturaComputarizadaCompraVenta>
"""
    return xml.encode("utf-8")
