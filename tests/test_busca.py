from unittest.mock import MagicMock

import pytest

import verbo.services.busca as busca


def _preparar_mocks(monkeypatch, resultado_query=None, erro_embeddings=None):
    client_mock = MagicMock()
    if erro_embeddings is not None:
        client_mock.embeddings.create.side_effect = erro_embeddings
    else:
        client_mock.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=[0.1, 0.2, 0.3])]
        )

    colecao_mock = MagicMock()
    if resultado_query is not None:
        colecao_mock.query.return_value = resultado_query

    monkeypatch.setattr(busca, "obter_client_nvidia", lambda: client_mock)
    monkeypatch.setattr(busca, "obter_colecao", lambda: colecao_mock)
    return client_mock, colecao_mock


def test_buscar_versiculos_propaga_erro_da_api(monkeypatch):
    """Se a API da NVIDIA falhar (ex.: 503 no free tier), a excecao deve
    subir para quem chamou, ja que app.py e responsavel por tratar isso."""
    _preparar_mocks(monkeypatch, erro_embeddings=RuntimeError("503 Service Unavailable"))

    with pytest.raises(RuntimeError):
        busca.buscar_versiculos("pergunta qualquer")


def test_buscar_versiculos_filtra_por_similaridade_minima(monkeypatch):
    resultado_query = {
        "documents": [["texto acima do limiar", "texto abaixo do limiar"]],
        "metadatas": [[{"referencia": "Genesis 1:1"}, {"referencia": "Genesis 1:2"}]],
        "distances": [[0.2, 1.9]],
    }
    _preparar_mocks(monkeypatch, resultado_query=resultado_query)

    versiculos = busca.buscar_versiculos("pergunta qualquer")

    assert len(versiculos) == 1
    assert versiculos[0]["referencia"] == "Genesis 1:1"
