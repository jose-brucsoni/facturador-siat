from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.domain.siat_ports import CuisResult, SiatAuthContext, WsdlNotConfiguredError
from src.infrastructure.db.models import CodigoOperacion
from src.infrastructure.siat.config import SiatSettings, POR_COMPLETAR, require_wsdl
from src.infrastructure.siat.evidence import save_soap_evidence
from src.infrastructure.siat.soap_client import SiatSoapClient
from src.infrastructure.siat.stub_client import StubSiatClient


def obtener_cuis(
    *,
    empresa_id: int,
    sucursal_id: int | None = None,
    punto_venta_id: int | None = None,
    client: StubSiatClient | SiatSoapClient | None = None,
    settings: SiatSettings | None = None,
) -> CodigoOperacion:
    settings = settings or SiatSettings.from_django()
    if client is None:
        if settings.modo == "stub":
            client = StubSiatClient()
        else:
            require_wsdl(settings.wsdl_codigos, "codigos")
            client = SiatSoapClient(settings)

    if isinstance(client, SiatSoapClient) and settings.wsdl_codigos == POR_COMPLETAR:
        raise WsdlNotConfiguredError("codigos")

    ctx = SiatAuthContext(
        token=settings.token,
        codigo_ambiente=settings.ambiente,
        codigo_sistema=settings.codigo_sistema,
        nit=settings.nit,
        codigo_modalidad=settings.modalidad,
        codigo_sucursal=int(settings.codigo_sucursal)
        if settings.codigo_sucursal != POR_COMPLETAR
        else 0,
        codigo_punto_venta=int(settings.codigo_punto_venta)
        if settings.codigo_punto_venta != POR_COMPLETAR
        else 0,
    )
    result: CuisResult = client.obtener_cuis(ctx)
    vigencia = result.vigencia_hasta or (
        datetime.now(timezone.utc) + timedelta(days=365)
    )
    codigo = CodigoOperacion.objects.create(
        empresa_id=empresa_id,
        sucursal_id=sucursal_id,
        punto_venta_id=punto_venta_id,
        tipo=CodigoOperacion.Tipo.CUIS,
        valor=result.codigo,
        vigencia_desde=datetime.now(timezone.utc),
        vigencia_hasta=vigencia,
        raw_request=result.exchange.request_xml,
        raw_response=result.exchange.response_xml,
    )
    save_soap_evidence(
        empresa_id=empresa_id,
        exchange=result.exchange,
        token=settings.token,
        tipo="cuis",
    )
    if result.mensaje_codigo == 3008:
        codigo.raw_response += "\n<!-- aviso: CUIS por vencer (3008) -->"
        codigo.save(update_fields=["raw_response"])
    return codigo
