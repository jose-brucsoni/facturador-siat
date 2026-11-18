from __future__ import annotations

from src.domain.siat_ports import ComunicacionResult, SinComunicacionError
from src.infrastructure.siat.config import SiatSettings, require_wsdl
from src.infrastructure.siat.soap_client import SiatSoapClient
from src.infrastructure.siat.stub_client import StubSiatClient


def verificar_comunicacion(
    *,
    resource: str = "codigos",
    client: StubSiatClient | SiatSoapClient | None = None,
    settings: SiatSettings | None = None,
) -> ComunicacionResult:
    settings = settings or SiatSettings.from_django()
    if client is None:
        if settings.modo == "stub":
            client = StubSiatClient()
        else:
            wsdl_map = {
                "codigos": settings.wsdl_codigos,
                "sincronizacion": settings.wsdl_sincronizacion,
                "operaciones": settings.wsdl_operaciones,
                "facturacion": settings.wsdl_facturacion,
            }
            require_wsdl(wsdl_map.get(resource, settings.wsdl_codigos), resource)
            client = SiatSoapClient(settings)

    if isinstance(client, StubSiatClient):
        result = client.verificar_comunicacion(resource)
    else:
        result = client.verificar_comunicacion(resource)

    if not result.ok:
        raise SinComunicacionError(resource, result.detail)
    return result
