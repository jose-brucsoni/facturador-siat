from __future__ import annotations

from dataclasses import dataclass

from src.infrastructure.siat.compression import CompressedPayload, gzip_and_hash
from src.infrastructure.siat.xml_builder import FacturaXmlInput, build_compra_venta_xml
from src.infrastructure.siat.xsd_validator import (
    ValidationResult,
    XsdMissingError,
    validate_xml,
)


@dataclass
class XmlBuildResult:
    xml_bytes: bytes
    compressed: CompressedPayload
    validation: ValidationResult | None
    xsd_missing: bool = False
    xsd_message: str = ""


def armar_xml_compra_venta(
    data: FacturaXmlInput, *, validate: bool = True
) -> XmlBuildResult:
    xml_bytes = build_compra_venta_xml(data)
    compressed = gzip_and_hash(xml_bytes)
    if not validate:
        return XmlBuildResult(xml_bytes=xml_bytes, compressed=compressed, validation=None)
    try:
        validation = validate_xml(xml_bytes)
        return XmlBuildResult(
            xml_bytes=xml_bytes, compressed=compressed, validation=validation
        )
    except XsdMissingError as exc:
        return XmlBuildResult(
            xml_bytes=xml_bytes,
            compressed=compressed,
            validation=None,
            xsd_missing=True,
            xsd_message=str(exc),
        )
