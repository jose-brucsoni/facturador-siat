"""Cálculos de montos de línea."""

from __future__ import annotations

from decimal import Decimal


def line_subtotal(
    cantidad: Decimal, precio_unitario: Decimal, descuento: Decimal = Decimal("0")
) -> Decimal:
    return (cantidad * precio_unitario) - descuento
