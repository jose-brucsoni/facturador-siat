from src.domain.cuf import (
    EJEMPLO_OFICIAL,
    EJEMPLO_OFICIAL_BASE16,
    EJEMPLO_OFICIAL_CUF,
    build_cadena_base,
    digito_verificador_mod11,
    generar_cuf,
    to_base16,
)


def test_cuf_ejemplo_oficial() -> None:
    cadena = build_cadena_base(EJEMPLO_OFICIAL)
    assert len(cadena) == 53
    dv = digito_verificador_mod11(cadena)
    assert to_base16(cadena + dv) == EJEMPLO_OFICIAL_BASE16
    assert generar_cuf(EJEMPLO_OFICIAL) == EJEMPLO_OFICIAL_CUF
