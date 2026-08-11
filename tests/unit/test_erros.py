import openai
import chromadb.errors

from verbo.core.erros import mensagem_erro_ia


class _RespostaFalsa:
    status_code = 401
    headers = {}
    request = None


def test_mensagem_erro_ia_para_falha_de_autenticacao():
    excecao = openai.AuthenticationError("chave invalida", response=_RespostaFalsa(), body=None)
    assert "autenticar" in mensagem_erro_ia(excecao)


def test_mensagem_erro_ia_para_banco_vetorial_indisponivel():
    excecao = chromadb.errors.NotFoundError("sem colecao")
    assert "base de versiculos" in mensagem_erro_ia(excecao)


def test_mensagem_erro_ia_para_erro_desconhecido():
    excecao = ValueError("algo generico")
    assert mensagem_erro_ia(excecao) == "Nao foi possivel completar a busca. Tente novamente."
