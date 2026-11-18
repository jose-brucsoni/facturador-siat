"""Datos compartidos para las pruebas."""

from __future__ import annotations

from decimal import Decimal

import pytest

from src.infrastructure.db.models import (
    Cliente,
    Empresa,
    Producto,
    PuntoVenta,
    Sucursal,
    User,
)


@pytest.fixture
def empresa_a(db) -> Empresa:
    return Empresa.objects.create(
        nit="1000001001",
        razon_social="Empresa A Demo",
        municipio="La Paz",
        modalidad=2,
    )


@pytest.fixture
def empresa_b(db) -> Empresa:
    return Empresa.objects.create(
        nit="1000002002",
        razon_social="Empresa B Demo",
        municipio="Santa Cruz",
        modalidad=2,
    )


@pytest.fixture
def sucursal_a(empresa_a: Empresa) -> Sucursal:
    return Sucursal.objects.create(
        empresa=empresa_a,
        codigo_sucursal=0,
        direccion="Av. Principal 100",
        municipio="La Paz",
    )


@pytest.fixture
def sucursal_b(empresa_b: Empresa) -> Sucursal:
    return Sucursal.objects.create(
        empresa=empresa_b,
        codigo_sucursal=0,
        direccion="Calle 1",
        municipio="Santa Cruz",
    )


@pytest.fixture
def pv_a(sucursal_a: Sucursal) -> PuntoVenta:
    return PuntoVenta.objects.create(
        sucursal=sucursal_a,
        codigo_punto_venta=0,
        nombre="Caja 1",
    )


@pytest.fixture
def pv_b(sucursal_b: Sucursal) -> PuntoVenta:
    return PuntoVenta.objects.create(
        sucursal=sucursal_b,
        codigo_punto_venta=0,
        nombre="Caja B",
    )


@pytest.fixture
def user_a(empresa_a: Empresa) -> User:
    return User.objects.create_user(
        username="cajero_a",
        password="pass",
        empresa=empresa_a,
        nombre_usuario="CAJEROA",
    )


@pytest.fixture
def user_b(empresa_b: Empresa) -> User:
    return User.objects.create_user(
        username="cajero_b",
        password="pass",
        empresa=empresa_b,
        nombre_usuario="CAJEROB",
    )


@pytest.fixture
def cliente_a(empresa_a: Empresa) -> Cliente:
    return Cliente.objects.create(
        empresa=empresa_a,
        codigo_cliente="C-A-1",
        tipo_documento_identidad=5,
        numero_documento="1234567",
        razon_social="Cliente A",
        email="cliente_a@example.com",
    )


@pytest.fixture
def cliente_b(empresa_b: Empresa) -> Cliente:
    return Cliente.objects.create(
        empresa=empresa_b,
        codigo_cliente="C-B-1",
        tipo_documento_identidad=5,
        numero_documento="7654321",
        razon_social="Cliente B",
        email="cliente_b@example.com",
    )


@pytest.fixture
def producto_a(empresa_a: Empresa) -> Producto:
    return Producto.objects.create(
        empresa=empresa_a,
        codigo_interno="P-A-1",
        descripcion="Producto A",
        actividad_economica="620100",
        codigo_producto_sin="83141",
        unidad_medida=58,
        precio_unitario=Decimal("100.00"),
    )
