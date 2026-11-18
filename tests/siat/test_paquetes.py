from src.infrastructure.siat.paquetes import MAX_FACTURAS_POR_PAQUETE, chunk_ids


def test_paquete_max_500() -> None:
    ids = list(range(501))
    chunks = chunk_ids(ids, MAX_FACTURAS_POR_PAQUETE)
    assert len(chunks) == 2
    assert len(chunks[0]) == 500
    assert len(chunks[1]) == 1
