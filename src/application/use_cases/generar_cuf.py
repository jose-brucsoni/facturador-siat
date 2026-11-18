from __future__ import annotations

from src.domain.cuf import CufInput, generar_cuf


def generar_cuf_factura(
    *,
    nit: int,
    fecha_hora: str,
    sucursal: int,
    modalidad: int,
    tipo_emision: int,
    tipo_factura: int,
    documento_sector: int,
    numero_factura: int,
    punto_venta: int,
    codigo_control: str,
) -> str:
    return generar_cuf(
        CufInput(
            nit=nit,
            fecha_hora=fecha_hora,
            sucursal=sucursal,
            modalidad=modalidad,
            tipo_emision=tipo_emision,
            tipo_factura=tipo_factura,
            documento_sector=documento_sector,
            numero_factura=numero_factura,
            punto_venta=punto_venta,
            codigo_control=codigo_control,
        )
    )
