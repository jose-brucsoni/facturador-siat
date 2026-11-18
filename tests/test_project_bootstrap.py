"""Pruebas de arranque del proyecto."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_agents_md_exists() -> None:
    assert (ROOT / "AGENTS.md").is_file()


def test_env_not_tracked_by_gitignore() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert re.search(r"(?m)^\.env$", gitignore) or ".env" in gitignore


def test_env_example_has_required_keys() -> None:
    content = (ROOT / ".env.example").read_text(encoding="utf-8")
    required = [
        "DATABASE_URL",
        "SIAT_AMBIENTE",
        "SIAT_NIT",
        "SIAT_CODIGO_SISTEMA",
        "SIAT_MODALIDAD",
        "SIAT_CODIGO_SUCURSAL",
        "SIAT_CODIGO_PUNTO_VENTA",
        "SIAT_TOKEN",
        "SIAT_WSDL_CODIGOS",
        "SIAT_WSDL_SINCRONIZACION",
        "SIAT_WSDL_OPERACIONES",
        "SIAT_WSDL_FACTURACION",
    ]
    for key in required:
        assert key in content, f"Falta {key} en .env.example"


def test_env_example_has_no_real_looking_token() -> None:
    content = (ROOT / ".env.example").read_text(encoding="utf-8")
    # Real delegated tokens are long opaque strings; placeholders are fine.
    for line in content.splitlines():
        if line.startswith("SIAT_TOKEN="):
            value = line.split("=", 1)[1].strip()
            assert value in {"POR_COMPLETAR", "", "change-me"} or value.startswith(
                "POR_"
            ), "SIAT_TOKEN no debe contener un secreto real en .env.example"
