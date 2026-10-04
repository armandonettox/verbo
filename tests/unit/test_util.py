import pytest

from verbo.core.util import separar_referencia


@pytest.mark.parametrize("referencia, esperado", [
    ("São Lucas 11:1-12", ("São Lucas", 11)),
    ("Gênesis 1:1", ("Gênesis", 1)),
    ("I Samuel 5:3-9", ("I Samuel", 5)),
    ("Atos dos Apóstolos 13:13-25", ("Atos dos Apóstolos", 13)),
    ("Cântico dos Cânticos 2:10", ("Cântico dos Cânticos", 2)),
])
def test_separa_livro_e_capitulo(referencia, esperado):
    assert separar_referencia(referencia) == esperado


@pytest.mark.parametrize("referencia", [
    "",
    "Gênesis",
    "Gênesis 1",
    "Gênesis 1,1",
    "1:1",
    "Gênesis um:1",
])
def test_formato_nao_reconhecido_devolve_none(referencia):
    assert separar_referencia(referencia) is None
