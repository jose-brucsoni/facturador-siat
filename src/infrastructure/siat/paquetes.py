"""Arma paquetes de facturas fuera de línea (máx. 500)."""

from __future__ import annotations

import gzip
import hashlib
from dataclasses import dataclass


MAX_FACTURAS_POR_PAQUETE = 500


@dataclass
class PaqueteBytes:
    gzip_bytes: bytes
    sha256_hex: str
    cantidad: int


def chunk_ids(factura_ids: list[int], size: int = MAX_FACTURAS_POR_PAQUETE) -> list[list[int]]:
    return [factura_ids[i : i + size] for i in range(0, len(factura_ids), size)]


def build_paquete_gzip(xml_list: list[bytes]) -> PaqueteBytes:
    # Une los XML y los comprime.
    raw = b"\n".join(xml_list)
    compressed = gzip.compress(raw)
    return PaqueteBytes(
        gzip_bytes=compressed,
        sha256_hex=hashlib.sha256(compressed).hexdigest(),
        cantidad=len(xml_list),
    )
