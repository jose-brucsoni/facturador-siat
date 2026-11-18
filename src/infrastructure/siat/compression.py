"""Comprime el XML y calcula su huella."""

from __future__ import annotations

import gzip
import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class CompressedPayload:
    gzip_bytes: bytes
    sha256_hex: str


def gzip_and_hash(xml_bytes: bytes) -> CompressedPayload:
    compressed = gzip.compress(xml_bytes)
    digest = hashlib.sha256(compressed).hexdigest()
    return CompressedPayload(gzip_bytes=compressed, sha256_hex=digest)
