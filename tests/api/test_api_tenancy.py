from __future__ import annotations

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_idor_entre_empresas(
    empresa_a, empresa_b, user_a, user_b, cliente_a, cliente_b
):
    c = APIClient()
    c.force_authenticate(user=user_a)
    r = c.get(f"/api/v1/clientes/{cliente_a.id}/")
    assert r.status_code == 200
    r = c.get(f"/api/v1/clientes/{cliente_b.id}/")
    assert r.status_code == 404

    r = c.get("/api/v1/clientes/")
    ids = [row["id"] for row in r.json()]
    assert cliente_a.id in ids
    assert cliente_b.id not in ids


@pytest.mark.django_db
def test_config_no_expone_token(user_a, settings):
    settings.SIAT_TOKEN = "SUPER-SECRET-TOKEN-SHOULD-NOT-LEAK"
    c = APIClient()
    c.force_authenticate(user=user_a)
    r = c.get("/api/v1/config/")
    assert r.status_code == 200
    body = r.content.decode()
    assert "SUPER-SECRET-TOKEN-SHOULD-NOT-LEAK" not in body
    assert "configurado" in body
