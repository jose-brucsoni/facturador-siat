"""Asignación del número de factura."""

from __future__ import annotations

from typing import Protocol


class InvoiceNumberAllocator(Protocol):
    def next_number(
        self, empresa_id: int, sucursal_id: int, punto_venta_id: int
    ) -> int: ...
