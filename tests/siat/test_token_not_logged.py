"""El token no debe aparecer en logs."""

from __future__ import annotations

import logging

import pytest

from src.infrastructure.db.models import TokenSiat
from src.infrastructure.siat.config import mask_token
from src.infrastructure.siat.logging_filters import MaskSiatTokenFilter


def test_mask_token():
    assert mask_token("POR_COMPLETAR") == "POR_COMPLETAR"
    masked = mask_token("abcdefghijklmnop")
    assert "***" in masked
    assert "efghijkl" not in masked


@pytest.mark.django_db
def test_token_not_logged(caplog, empresa_a):
    secret = "SUPER-SECRET-TOKEN-ABC123XYZ"
    TokenSiat.objects.create(empresa=empresa_a, token_cifrado="cipher")
    logger = logging.getLogger("siat_test_token")
    logger.addFilter(MaskSiatTokenFilter())
    logger.setLevel(logging.INFO)
    with caplog.at_level(logging.INFO, logger="siat_test_token"):
        logger.info("apikey=TokenApi %s", secret)
    assert secret not in caplog.text
    assert "TokenApi ***" in caplog.text or "***" in caplog.text


@pytest.mark.django_db
def test_token_model_str_hides_value(empresa_a):
    t = TokenSiat.objects.create(empresa=empresa_a, token_cifrado="cipher-secret")
    assert "cipher-secret" not in str(t)
