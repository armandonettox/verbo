import numpy as np
import pytest

from verbo.core import embedding_local


class _ModeloFalso:
    def __init__(self):
        self.recebidos = []

    def embed(self, textos):
        self.recebidos.extend(textos)
        return [np.array([1.0, 0.0]) for _ in textos]


@pytest.fixture
def modelo_falso(monkeypatch):
    falso = _ModeloFalso()
    monkeypatch.setattr(embedding_local, "_modelo", falso)
    return falso


def test_query_recebe_prefixo_query(modelo_falso):
    gerar = embedding_local.gerar_embeddings
    gerar(["o que e o perdao?"], "query")
    assert modelo_falso.recebidos == ["query: o que e o perdao?"]


def test_passage_recebe_prefixo_passage(modelo_falso):
    embedding_local.gerar_embeddings(["No principio..."], "passage")
    assert modelo_falso.recebidos == ["passage: No principio..."]


def test_retorna_listas_de_float(modelo_falso):
    resultado = embedding_local.gerar_embeddings(["a", "b"], "passage")
    assert resultado == [[1.0, 0.0], [1.0, 0.0]]


def test_tipo_invalido_levanta_erro(modelo_falso):
    with pytest.raises(ValueError):
        embedding_local.gerar_embeddings(["a"], "outro")
