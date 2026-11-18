"""Pruebas del número de factura."""

from __future__ import annotations

import pytest
from django.db import transaction

from src.infrastructure.db.models import InvoiceCounter


@pytest.mark.django_db
def test_allocate_increments_per_pv(empresa_a, sucursal_a, pv_a):
    n1 = InvoiceCounter.allocate(empresa_a.id, sucursal_a.id, pv_a.id)
    n2 = InvoiceCounter.allocate(empresa_a.id, sucursal_a.id, pv_a.id)
    assert n1 == 1
    assert n2 == 2


@pytest.mark.django_db
def test_two_cashiers_simulated_transaction(empresa_a, sucursal_a, pv_a):
    """Dos cajeros no deben obtener el mismo número."""
    numbers: list[int] = []
    for _ in range(2):
        with transaction.atomic():
            numbers.append(InvoiceCounter.allocate(empresa_a.id, sucursal_a.id, pv_a.id))
    assert numbers == [1, 2]
    assert len(set(numbers)) == 2
