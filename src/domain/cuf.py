"""Genera el código único de factura (CUF)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CufInput:
    nit: int
    fecha_hora: str  # yyyyMMddHHmmssSSS (17)
    sucursal: int
    modalidad: int
    tipo_emision: int
    tipo_factura: int
    documento_sector: int
    numero_factura: int
    punto_venta: int
    codigo_control: str


def digito_verificador_mod11(cadena: str) -> str:
    """Calcula el dígito de control módulo 11."""
    mult = 2
    total = 0
    for ch in reversed(cadena):
        total += int(ch) * mult
        mult += 1
        if mult > 9:
            mult = 2
    resto = total % 11
    digito = 11 - resto
    if digito == 11:
        return "0"
    if digito == 10:
        return "1"
    return str(digito)


def build_cadena_base(data: CufInput) -> str:
    if len(data.fecha_hora) != 17 or not data.fecha_hora.isdigit():
        raise ValueError("fecha_hora debe tener 17 dígitos (yyyyMMddHHmmssSSS).")
    parts = [
        f"{data.nit:013d}",
        data.fecha_hora,
        f"{data.sucursal:04d}",
        f"{data.modalidad:01d}",
        f"{data.tipo_emision:01d}",
        f"{data.tipo_factura:01d}",
        f"{data.documento_sector:02d}",
        f"{data.numero_factura:010d}",
        f"{data.punto_venta:04d}",
    ]
    cadena = "".join(parts)
    if len(cadena) != 53:
        raise ValueError(f"Cadena base debe tener 53 dígitos, obtuvo {len(cadena)}")
    return cadena


def to_base16(cadena_con_dv: str) -> str:
    return format(int(cadena_con_dv), "X")


def generar_cuf(data: CufInput) -> str:
    cadena = build_cadena_base(data)
    dv = digito_verificador_mod11(cadena)
    base16 = to_base16(cadena + dv)
    return base16 + data.codigo_control


# Ejemplo oficial usado en las pruebas.
EJEMPLO_OFICIAL = CufInput(
    nit=123456789,
    fecha_hora="20190113163721231",
    sucursal=0,
    modalidad=1,
    tipo_emision=1,
    tipo_factura=1,
    documento_sector=1,
    numero_factura=1,
    punto_venta=0,
    codigo_control="A19E23EF34124CD",
)
EJEMPLO_OFICIAL_BASE16 = "8727F63A15F8976591FDDE5B387C5D015A29E06A1"
EJEMPLO_OFICIAL_CUF = EJEMPLO_OFICIAL_BASE16 + "A19E23EF34124CD"
