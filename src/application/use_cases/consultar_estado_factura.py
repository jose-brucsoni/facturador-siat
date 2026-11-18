from __future__ import annotations

from src.domain.siat_ports import SiatAuthContext
from src.domain.tenancy import assert_same_empresa
from src.infrastructure.db.models import Factura
from src.infrastructure.siat.config import SiatSettings, POR_COMPLETAR
from src.infrastructure.siat.evidence import save_soap_evidence
from src.infrastructure.siat.recepcion import consultar_estado
from src.infrastructure.siat.stub_client import StubSiatClient


def consultar_estado_factura(
    *,
    empresa_id: int,
    factura_id: int | None = None,
    cuf: str | None = None,
    client: StubSiatClient | None = None,
    settings: SiatSettings | None = None,
) -> dict:
    settings = settings or SiatSettings.from_django()
    client = client or StubSiatClient()

    if factura_id:
        factura = Factura.objects.get(pk=factura_id)
        assert_same_empresa(factura.empresa_id, empresa_id)
        cuf = factura.cuf
    elif cuf:
        factura = Factura.objects.get(empresa_id=empresa_id, cuf=cuf)
    else:
        raise ValueError("Indique factura_id o cuf.")

    ctx = SiatAuthContext(
        token=settings.token if settings.token != POR_COMPLETAR else "stub",
        codigo_ambiente=settings.ambiente,
        codigo_sistema=settings.codigo_sistema,
        nit=settings.nit if settings.nit != POR_COMPLETAR else "0",
        codigo_modalidad=settings.modalidad,
    )
    result = consultar_estado(client, ctx, cuf or "")
    exchange = result.get("exchange")
    if exchange:
        save_soap_evidence(
            empresa_id=empresa_id,
            factura_id=factura.id,
            exchange=exchange,
            token=settings.token,
            tipo="consulta_estado",
        )
    codigo = str(result.get("codigoEstado", ""))
    factura.estado_siat = codigo
    factura.save(update_fields=["estado_siat", "updated_at"])
    return {"factura_id": factura.id, "cuf": factura.cuf, "codigoEstado": codigo}


def nota_credito_debito_no_implementada() -> None:
    """Nota crédito-débito: aún no disponible."""
    raise NotImplementedError("Nota Crédito-Débito aún no implementada.")
