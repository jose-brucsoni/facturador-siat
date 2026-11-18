from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_piloto_checklist_presente() -> None:
    path = ROOT / "docs" / "piloto-checklist.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "Fase I" in text
    assert "Fase II" in text
    assert "Fase III" in text
    assert "POR_COMPLETAR" in text
    assert "102600000045" in text or "RND 102600000045" in text
