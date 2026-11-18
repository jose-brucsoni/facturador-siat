"""Pruebas básicas de modelos."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.db import IntegrityError

from src.domain.money import line_subtotal
from src.infrastructure.db.models import Empresa, Sucursal


def test_nit_empresa_unique(db):
    Empresa.objects.create(nit="999", razon_social="Uno")
    with pytest.raises(IntegrityError):
        Empresa.objects.create(nit="999", razon_social="Dos")


def test_sucursal_cero_casa_matriz_permitida(empresa_a):
    s = Sucursal.objects.create(
        empresa=empresa_a,
        codigo_sucursal=0,
        direccion="Casa Matriz",
    )
    assert s.codigo_sucursal == 0


def test_detalle_subtotal_coherente():
    assert line_subtotal(Decimal("2"), Decimal("10.5"), Decimal("1")) == Decimal("20.0")
