"""Contratos de comunicación con el SIN."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol


class WsdlNotConfiguredError(Exception):
    """Faltan las direcciones de conexión al SIN."""

    def __init__(
        self,
        resource: str = "WSDL",
        message: str | None = None,
    ) -> None:
        self.resource = resource
        super().__init__(
            message
            or (
                f"WSDL no configurado ({resource}): pega las URLs del "
                "reporte oficial de autorización del SIN."
            )
        )


class SinComunicacionError(Exception):
    """No hay comunicación con el SIN."""

    def __init__(self, resource: str, detail: str = "") -> None:
        self.resource = resource
        super().__init__(f"Sin comunicación con el SIN ({resource}). {detail}".strip())


@dataclass
class SiatAuthContext:
    token: str
    codigo_ambiente: str
    codigo_sistema: str
    nit: str
    codigo_modalidad: int = 2
    codigo_sucursal: int = 0
    codigo_punto_venta: int = 0
    cuis: str | None = None


@dataclass
class SoapExchange:
    request_xml: str
    response_xml: str
    method: str
    resource: str


@dataclass
class CuisResult:
    codigo: str
    vigencia_hasta: datetime | None
    exchange: SoapExchange
    mensaje_codigo: int | None = None


@dataclass
class CufdResult:
    codigo: str
    codigo_control: str
    vigencia_hasta: datetime | None
    exchange: SoapExchange


@dataclass
class CatalogItem:
    tipo: str
    codigo: str
    descripcion: str
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class CatalogSyncResult:
    items: list[CatalogItem]
    exchange: SoapExchange


@dataclass
class ComunicacionResult:
    ok: bool
    resource: str
    exchange: SoapExchange | None = None
    detail: str = ""


class ISiatCodigosClient(Protocol):
    def obtener_cuis(self, ctx: SiatAuthContext) -> CuisResult: ...

    def solicitar_cufd(self, ctx: SiatAuthContext) -> CufdResult: ...

    def verificar_comunicacion(self) -> ComunicacionResult: ...


class ISiatSincronizacionClient(Protocol):
    def sincronizar(self, ctx: SiatAuthContext, metodo: str) -> CatalogSyncResult: ...

    def verificar_comunicacion(self) -> ComunicacionResult: ...


class ISiatOperacionesClient(Protocol):
    def verificar_comunicacion(self) -> ComunicacionResult: ...


class ISiatFacturacionClient(Protocol):
    def verificar_comunicacion(self) -> ComunicacionResult: ...

    def recepcion_factura(self, ctx: SiatAuthContext, payload: dict[str, Any]) -> Any: ...

    def verificacion_estado_factura(
        self, ctx: SiatAuthContext, cuf: str
    ) -> Any: ...

    def anular_factura(self, ctx: SiatAuthContext, payload: dict[str, Any]) -> Any: ...


class IXmlSigner(Protocol):
    """Firma electrónica (aún no usada en esta versión)."""

    def sign(self, xml_bytes: bytes) -> bytes: ...


class INotifier(Protocol):
    def send_email(
        self, to: str, subject: str, body: str, attachments: list[tuple[str, bytes]] | None = None
    ) -> None: ...
