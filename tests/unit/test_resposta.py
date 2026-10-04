import httpx
import openai
import pytest

from verbo.core import resposta
from verbo.core.erros import IAInstavelError, mensagem_erro_ia

VERSICULOS = [{"referencia": "Livro 1:1", "texto": "texto", "similaridade": 50}]


class _ClienteFalso:
    def __init__(self, erro=None, texto="resposta"):
        self.chamadas = 0
        self._erro = erro
        self._texto = texto
        self.chat = self
        self.completions = self

    def create(self, **kwargs):
        self.chamadas += 1
        if self._erro:
            raise self._erro
        mensagem = type("M", (), {"content": self._texto})
        return type("R", (), {"choices": [type("C", (), {"message": mensagem})]})


def _timeout():
    return openai.APITimeoutError(request=httpx.Request("POST", "https://x"))


def test_resposta_normal_devolve_texto_e_registra_latencia(monkeypatch):
    monkeypatch.setattr(resposta, "_obter_client", lambda: _ClienteFalso())
    assert resposta.gerar_resposta("pergunta", VERSICULOS) == "resposta"
    assert resposta.metricas.resumo()["latencias"]["chat"]["quantidade"] == 1


def test_cliente_do_chat_tem_timeout_e_sem_retry(monkeypatch):
    criados = []
    monkeypatch.setattr(resposta, "_client", None)
    monkeypatch.setattr(resposta, "OpenAI", lambda **kw: criados.append(kw) or object())
    resposta._obter_client()
    assert criados[0]["timeout"] == resposta.CHAT_TIMEOUT_SEGUNDOS
    assert criados[0]["max_retries"] == 0


def test_duas_falhas_abrem_o_disjuntor_e_a_terceira_nem_chama(monkeypatch):
    cliente = _ClienteFalso(erro=_timeout())
    monkeypatch.setattr(resposta, "_obter_client", lambda: cliente)

    for _ in range(2):
        with pytest.raises(openai.APITimeoutError):
            resposta.gerar_resposta("pergunta", VERSICULOS)
    with pytest.raises(IAInstavelError):
        resposta.gerar_resposta("pergunta", VERSICULOS)

    assert cliente.chamadas == 2
    contadores = resposta.metricas.resumo()["contadores"]
    assert contadores["chat_falha"] == 2
    assert contadores["chat_disjuntor_aberto"] == 1


def test_continuar_conversa_tambem_passa_pelo_disjuntor(monkeypatch):
    cliente = _ClienteFalso(erro=_timeout())
    monkeypatch.setattr(resposta, "_obter_client", lambda: cliente)
    for _ in range(2):
        with pytest.raises(openai.APITimeoutError):
            resposta.continuar_conversa("p", "r", VERSICULOS, [], "nova")
    with pytest.raises(IAInstavelError):
        resposta.continuar_conversa("p", "r", VERSICULOS, [], "nova")


def test_erro_que_nao_e_da_ia_nao_conta_como_falha(monkeypatch):
    monkeypatch.setattr(resposta, "_obter_client", lambda: _ClienteFalso(erro=KeyError("bug")))
    for _ in range(3):
        with pytest.raises(KeyError):
            resposta.gerar_resposta("pergunta", VERSICULOS)
    assert resposta.disjuntor.estado == "fechado"


def test_mensagem_de_timeout_e_diferente_da_de_conexao():
    assert "demorou" in mensagem_erro_ia(_timeout())
    conexao = openai.APIConnectionError(request=httpx.Request("POST", "https://x"))
    assert "conectar" in mensagem_erro_ia(conexao)


def test_mensagem_de_ia_instavel():
    assert "instavel" in mensagem_erro_ia(IAInstavelError())
