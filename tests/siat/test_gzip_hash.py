from __future__ import annotations

import hashlib

from src.infrastructure.siat.compression import gzip_and_hash


def test_gzip_sha256() -> None:
    payload = b"<xml>demo</xml>"
    result = gzip_and_hash(payload)
    assert result.gzip_bytes.startswith(b"\x1f\x8b")
    assert result.sha256_hex == hashlib.sha256(result.gzip_bytes).hexdigest()
    # Must hash gzip, not plain XML
    assert result.sha256_hex != hashlib.sha256(payload).hexdigest()
