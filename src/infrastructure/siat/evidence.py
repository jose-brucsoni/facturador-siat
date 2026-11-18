"""Guarda las evidencias de comunicación con el SIN."""

from __future__ import annotations

from src.domain.siat_ports import SoapExchange
from src.infrastructure.db.models import FacturaEvidencia
from src.infrastructure.siat.config import mask_token


def _scrub(xml: str, token: str | None) -> str:
    if not token or token == "POR_COMPLETAR":
        return xml
    return xml.replace(token, mask_token(token))


def save_soap_evidence(
    *,
    empresa_id: int,
    exchange: SoapExchange,
    factura_id: int | None = None,
    token: str | None = None,
    tipo: str = "soap",
) -> FacturaEvidencia:
    return FacturaEvidencia.objects.create(
        empresa_id=empresa_id,
        factura_id=factura_id,
        tipo=tipo,
        soap_request=_scrub(exchange.request_xml, token),
        soap_response=_scrub(exchange.response_xml, token),
        metadata={"method": exchange.method, "resource": exchange.resource},
    )
