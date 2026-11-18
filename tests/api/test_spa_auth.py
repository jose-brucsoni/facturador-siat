from __future__ import annotations

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_csrf_sets_cookie():
    c = APIClient(enforce_csrf_checks=False)
    r = c.get("/api/v1/csrf/")
    assert r.status_code == 200
    assert "csrfToken" in r.json()


@pytest.mark.django_db
def test_login_me_logout(user_a, empresa_a):
    c = APIClient()
    r = c.post(
        "/api/v1/login/",
        data={"username": "cajero_a", "password": "pass"},
        format="json",
    )
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == user_a.username
    assert body["empresa_id"] == empresa_a.id
    assert body["empresa_razon_social"] == empresa_a.razon_social

    me = c.get("/api/v1/me/")
    assert me.status_code == 200
    assert me.json()["empresa_id"] == empresa_a.id

    out = c.post("/api/v1/logout/")
    assert out.status_code == 200

    me2 = c.get("/api/v1/me/")
    assert me2.status_code in (401, 403)


@pytest.mark.django_db
def test_me_requires_auth():
    c = APIClient()
    r = c.get("/api/v1/me/")
    assert r.status_code in (401, 403)


@pytest.mark.django_db
def test_sucursales_aisladas(user_a, user_b, sucursal_a, sucursal_b, pv_a):
    c = APIClient()
    c.force_authenticate(user=user_a)
    r = c.get("/api/v1/sucursales/")
    assert r.status_code == 200
    ids = [row["id"] for row in r.json()]
    assert sucursal_a.id in ids
    assert sucursal_b.id not in ids
    row = next(x for x in r.json() if x["id"] == sucursal_a.id)
    assert any(pv["id"] == pv_a.id for pv in row["puntos_venta"])

    c.force_authenticate(user=user_b)
    r = c.get("/api/v1/sucursales/")
    ids = [row["id"] for row in r.json()]
    assert sucursal_b.id in ids
    assert sucursal_a.id not in ids
