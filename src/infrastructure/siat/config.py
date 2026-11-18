"""Lee la configuración del SIN desde el entorno."""

from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings

from src.domain.siat_ports import WsdlNotConfiguredError

POR_COMPLETAR = "POR_COMPLETAR"


@dataclass(frozen=True)
class SiatSettings:
    modo: str
    ambiente: str
    nit: str
    codigo_sistema: str
    modalidad: int
    codigo_sucursal: str
    codigo_punto_venta: str
    token: str
    wsdl_codigos: str
    wsdl_sincronizacion: str
    wsdl_operaciones: str
    wsdl_facturacion: str
    qr_base_url: str
    timeout_seconds: int

    @classmethod
    def from_django(cls) -> SiatSettings:
        return cls(
            modo=getattr(settings, "SIAT_MODO", "stub"),
            ambiente=getattr(settings, "SIAT_AMBIENTE", POR_COMPLETAR),
            nit=getattr(settings, "SIAT_NIT", POR_COMPLETAR),
            codigo_sistema=getattr(settings, "SIAT_CODIGO_SISTEMA", POR_COMPLETAR),
            modalidad=int(getattr(settings, "SIAT_MODALIDAD", 2)),
            codigo_sucursal=str(getattr(settings, "SIAT_CODIGO_SUCURSAL", POR_COMPLETAR)),
            codigo_punto_venta=str(
                getattr(settings, "SIAT_CODIGO_PUNTO_VENTA", POR_COMPLETAR)
            ),
            token=getattr(settings, "SIAT_TOKEN", POR_COMPLETAR),
            wsdl_codigos=getattr(settings, "SIAT_WSDL_CODIGOS", POR_COMPLETAR),
            wsdl_sincronizacion=getattr(
                settings, "SIAT_WSDL_SINCRONIZACION", POR_COMPLETAR
            ),
            wsdl_operaciones=getattr(settings, "SIAT_WSDL_OPERACIONES", POR_COMPLETAR),
            wsdl_facturacion=getattr(settings, "SIAT_WSDL_FACTURACION", POR_COMPLETAR),
            qr_base_url=getattr(
                settings,
                "SIAT_QR_BASE_URL",
                "https://pilotosiat.impuestos.gob.bo/consulta/QR",
            ),
            timeout_seconds=int(getattr(settings, "SIAT_TIMEOUT_SECONDS", 30)),
        )


def require_wsdl(url: str, resource: str) -> str:
    if not url or url.strip() == POR_COMPLETAR:
        raise WsdlNotConfiguredError(resource=resource)
    return url


def mask_token(value: str) -> str:
    if not value or value == POR_COMPLETAR:
        return value
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}***{value[-4:]}"


def apikey_header(token: str) -> str:
    """Arma el encabezado de autenticación."""
    return f"TokenApi {token}"
