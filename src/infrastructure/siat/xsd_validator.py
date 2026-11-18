"""Valida el XML contra el esquema oficial de Compra-Venta."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from lxml import etree


XSD_DOWNLOAD_URL = (
    "https://siatinfo.impuestos.gob.bo/index.php/facturacion-en-linea/"
    "archivos-xml-xsd-de-facturas-electronicas/factura-de-compra-y-venta"
)


class XsdMissingError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Falta el XSD oficial en schemas/compra_venta.xsd. "
            f"Descárgalo desde: {XSD_DOWNLOAD_URL}"
        )


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def xsd_path() -> Path:
    base = Path(getattr(settings, "SIAT_SCHEMAS_DIR", Path("schemas")))
    return base / "compra_venta.xsd"


def validate_xml(xml_bytes: bytes) -> ValidationResult:
    path = xsd_path()
    if not path.is_file() or path.stat().st_size == 0:
        raise XsdMissingError()
    schema_doc = etree.parse(str(path))
    schema = etree.XMLSchema(schema_doc)
    doc = etree.fromstring(xml_bytes)
    ok = schema.validate(doc)
    errors = [str(e) for e in schema.error_log] if not ok else []
    return ValidationResult(ok=ok, errors=errors)
