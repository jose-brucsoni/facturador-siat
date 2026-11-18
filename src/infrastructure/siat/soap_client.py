"""Cliente SOAP real hacia el SIN (solo si hay URLs configuradas)."""

from __future__ import annotations

import logging
from typing import Any

from src.domain.siat_ports import (
    ComunicacionResult,
    CufdResult,
    CuisResult,
    SiatAuthContext,
    SoapExchange,
    WsdlNotConfiguredError,
)
from src.infrastructure.siat.config import (
    SiatSettings,
    apikey_header,
    mask_token,
    require_wsdl,
)

logger = logging.getLogger(__name__)


class SiatSoapClient:
    """Conexión SOAP con el SIN."""

    def __init__(self, settings: SiatSettings | None = None) -> None:
        self.settings = settings or SiatSettings.from_django()
        self._clients: dict[str, Any] = {}

    def _get_client(self, resource: str, wsdl_url: str):
        require_wsdl(wsdl_url, resource)
        if resource not in self._clients:
            from zeep import Client
            from zeep.transports import Transport

            session_headers = {"apikey": apikey_header(self.settings.token)}
            transport = Transport(timeout=self.settings.timeout_seconds)
            client = Client(wsdl_url, transport=transport)
            client.transport.session.headers.update(session_headers)
            self._clients[resource] = client
            logger.info(
                "SIAT SOAP client created for %s (token=%s)",
                resource,
                mask_token(self.settings.token),
            )
        return self._clients[resource]

    def verificar_comunicacion(self, resource: str = "codigos") -> ComunicacionResult:
        wsdl_map = {
            "codigos": self.settings.wsdl_codigos,
            "sincronizacion": self.settings.wsdl_sincronizacion,
            "operaciones": self.settings.wsdl_operaciones,
            "facturacion": self.settings.wsdl_facturacion,
        }
        wsdl = wsdl_map.get(resource, self.settings.wsdl_codigos)
        try:
            client = self._get_client(resource, wsdl)
        except WsdlNotConfiguredError:
            raise
        try:
            result = client.service.verificarComunicacion()
            ok = bool(result) and result not in (False, -1, "-1")
            return ComunicacionResult(
                ok=ok,
                resource=resource,
                exchange=SoapExchange(
                    request_xml="<verificarComunicacion/>",
                    response_xml=str(result),
                    method="verificarComunicacion",
                    resource=resource,
                ),
            )
        except Exception as exc:  # noqa: BLE001
            return ComunicacionResult(ok=False, resource=resource, detail=str(exc))

    def obtener_cuis(self, ctx: SiatAuthContext) -> CuisResult:
        raise WsdlNotConfiguredError("codigos")

    def solicitar_cufd(self, ctx: SiatAuthContext) -> CufdResult:
        raise WsdlNotConfiguredError("codigos")
