"""Envío, consulta y anulación de facturas ante el SIN."""

from __future__ import annotations

from typing import Any

from src.domain.siat_ports import SiatAuthContext
from src.infrastructure.siat.stub_client import StubSiatClient


def recepcion_factura(
    client: StubSiatClient, ctx: SiatAuthContext, payload: dict[str, Any]
) -> dict[str, Any]:
    # Envío de la factura al SIN.
    return client.recepcion_factura(ctx, payload)


def consultar_estado(
    client: StubSiatClient, ctx: SiatAuthContext, cuf: str
) -> dict[str, Any]:
    # Consulta el estado de una factura.
    return client.verificacion_estado_factura(ctx, cuf)


def anular_factura(
    client: StubSiatClient, ctx: SiatAuthContext, payload: dict[str, Any]
) -> dict[str, Any]:
    # Solicita la anulación de una factura.
    return client.anular_factura(ctx, payload)
