from __future__ import annotations

from src.domain.siat_ports import SiatAuthContext, WsdlNotConfiguredError
from src.infrastructure.db.models import CatalogoSiat
from src.infrastructure.siat.config import SiatSettings, POR_COMPLETAR, require_wsdl
from src.infrastructure.siat.evidence import save_soap_evidence
from src.infrastructure.siat.soap_client import SiatSoapClient
from src.infrastructure.siat.stub_client import StubSiatClient

DEFAULT_SYNC_METHODS = (
    "sincronizarListaLeyendasFactura",
    "sincronizarParametricaTipoFactura",
    "sincronizarParametricaTipoMetodoPago",
)


def sincronizar_catalogos(
    *,
    empresa_id: int,
    metodos: tuple[str, ...] = DEFAULT_SYNC_METHODS,
    client: StubSiatClient | SiatSoapClient | None = None,
    settings: SiatSettings | None = None,
) -> list[CatalogoSiat]:
    settings = settings or SiatSettings.from_django()
    if client is None:
        if settings.modo == "stub":
            client = StubSiatClient()
        else:
            require_wsdl(settings.wsdl_sincronizacion, "sincronizacion")
            raise WsdlNotConfiguredError("sincronizacion")

    if isinstance(client, SiatSoapClient):
        raise WsdlNotConfiguredError("sincronizacion")

    ctx = SiatAuthContext(
        token=settings.token,
        codigo_ambiente=settings.ambiente,
        codigo_sistema=settings.codigo_sistema,
        nit=settings.nit,
        codigo_modalidad=settings.modalidad,
    )
    upserted: list[CatalogoSiat] = []
    for metodo in metodos:
        result = client.sincronizar(ctx, metodo)
        for item in result.items:
            obj, _ = CatalogoSiat.objects.update_or_create(
                empresa_id=empresa_id,
                tipo=item.tipo,
                codigo=item.codigo,
                defaults={
                    "descripcion": item.descripcion,
                    "json_extra": item.extra,
                },
            )
            upserted.append(obj)
        save_soap_evidence(
            empresa_id=empresa_id,
            exchange=result.exchange,
            token=settings.token,
            tipo=f"catalogo:{metodo}",
        )
    return upserted
