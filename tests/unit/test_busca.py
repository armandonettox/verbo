import httpx
import openai
import pytest

from verbo.core import busca


def _resultados(distancias):
    return {
        "documents": [[f"texto {i}" for i in range(len(distancias))]],
        "metadatas": [[{"referencia": f"Livro 1:{i}"} for i in range(len(distancias))]],
        "distances": [distancias],
    }


def test_formatar_converte_distancia_em_similaridade():
    versiculos = busca._formatar(_resultados([0.0, 0.4]))
    assert versiculos[0]["similaridade"] == 100.0
    assert versiculos[1]["similaridade"] == 80.0
    assert versiculos[1]["referencia"] == "Livro 1:1"


def test_formatar_corta_abaixo_do_minimo():
    # distancia 1.0 equivale a 50%, distancia 1.4 a 30%
    versiculos = busca._formatar(_resultados([0.2, 1.0, 1.4]), similaridade_minima=40)
    assert [v["similaridade"] for v in versiculos] == [90.0, 50.0]


def test_formatar_sem_minimo_mantem_todos():
    versiculos = busca._formatar(_resultados([0.2, 1.0, 1.4]))
    assert len(versiculos) == 3


def test_fallback_usa_nvidia_quando_funciona(monkeypatch):
    monkeypatch.setattr(busca, "buscar_versiculos", lambda p: [{"referencia": "nv"}])
    monkeypatch.setattr(busca, "buscar_versiculos_local", lambda p: pytest.fail("nao deveria chamar"))

    resultado = busca.buscar_com_fallback("pergunta")

    assert resultado == {"versiculos": [{"referencia": "nv"}], "modo": "nvidia"}


@pytest.mark.parametrize("erro", [
    openai.OpenAIError("sem chave"),
    openai.APIConnectionError(request=httpx.Request("POST", "https://x")),
    openai.APITimeoutError(request=httpx.Request("POST", "https://x")),
])
def test_fallback_cai_para_local_quando_nvidia_falha(monkeypatch, erro):
    def nvidia_falha(pergunta):
        raise erro

    monkeypatch.setattr(busca, "buscar_versiculos", nvidia_falha)
    monkeypatch.setattr(busca, "buscar_versiculos_local", lambda p: [{"referencia": "local"}])

    resultado = busca.buscar_com_fallback("pergunta")

    assert resultado == {"versiculos": [{"referencia": "local"}], "modo": "local"}


def test_erro_inesperado_nao_aciona_fallback(monkeypatch):
    def nvidia_falha(pergunta):
        raise KeyError("bug de codigo")

    monkeypatch.setattr(busca, "buscar_versiculos", nvidia_falha)
    monkeypatch.setattr(busca, "buscar_versiculos_local", lambda p: pytest.fail("nao deveria chamar"))

    with pytest.raises(KeyError):
        busca.buscar_com_fallback("pergunta")


def test_se_o_local_tambem_falha_o_erro_sobe(monkeypatch):
    def nvidia_falha(pergunta):
        raise openai.OpenAIError("fora do ar")

    def local_falha(pergunta):
        raise RuntimeError("indice local ausente")

    monkeypatch.setattr(busca, "buscar_versiculos", nvidia_falha)
    monkeypatch.setattr(busca, "buscar_versiculos_local", local_falha)

    with pytest.raises(RuntimeError):
        busca.buscar_com_fallback("pergunta")
