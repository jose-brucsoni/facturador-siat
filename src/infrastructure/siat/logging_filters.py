"""Oculta el token del SIN en los logs."""

from __future__ import annotations

import logging
import re

_TOKEN_PATTERN = re.compile(r"(TokenApi\s+)\S+", re.IGNORECASE)


class MaskSiatTokenFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            formatted = record.getMessage()
        except Exception:
            return True
        if "TokenApi" in formatted or "SIAT_TOKEN" in formatted:
            record.msg = _TOKEN_PATTERN.sub(r"\1***", formatted)
            record.args = ()
        return True
