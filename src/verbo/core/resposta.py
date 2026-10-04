import time

import openai
from openai import OpenAI
from verbo.config import (
    NVIDIA_API_KEY, CHAT_MODEL, CHAT_TIMEOUT_SEGUNDOS,
    DISJUNTOR_FALHAS, DISJUNTOR_PAUSA_SEGUNDOS,
)
from verbo.core import metricas
from verbo.core.disjuntor import Disjuntor
from verbo.core.erros import IAInstavelError

# Mudou o texto do prompt? Suba a versao para nao reaproveitar respostas antigas
PROMPT_VERSAO = "1"

_client = None
disjuntor = Disjuntor(DISJUNTOR_FALHAS, DISJUNTOR_PAUSA_SEGUNDOS)


def _obter_client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=NVIDIA_API_KEY,
            base_url="https://integrate.api.nvidia.com/v1",
            # sem retry: o tempo total fica limitado ao timeout
            timeout=CHAT_TIMEOUT_SEGUNDOS,
            max_retries=0,
        )
    return _client


def _chamar_chat(messages: list[dict]) -> str:
    if not disjuntor.permite():
        metricas.contar("chat_disjuntor_aberto")
        raise IAInstavelError()

    inicio = time.monotonic()
    try:
        resposta = _obter_client().chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
        )
    except openai.OpenAIError:
        disjuntor.registrar_falha()
        metricas.contar("chat_falha")
        raise

    disjuntor.registrar_sucesso()
    metricas.registrar_latencia("chat", time.monotonic() - inicio)
    return resposta.choices[0].message.content


def _montar_contexto(versiculos: list[dict]) -> str:
    return "\n".join(
        f"{v['referencia']}: {v['texto']}" for v in versiculos
    )


def gerar_resposta(pergunta: str, versiculos: list[dict]) -> str:
    contexto = _montar_contexto(versiculos)

    prompt = f"""Voce e um assistente que responde perguntas usando EXCLUSIVAMENTE os versiculos da Biblia fornecidos abaixo.
Nao use conhecimento proprio nem invente nada fora dos versiculos.

Sintetize uma resposta clara em portugues juntando as informacoes relevantes dos versiculos,
em vez de apenas citar um unico versiculo isolado. Cite as referencias (livro, capitulo e versiculo)
que embasam cada parte da resposta. Se nenhum versiculo responder a pergunta, diga isso claramente.

Versiculos:
{contexto}

Pergunta: {pergunta}

Resposta:"""

    return _chamar_chat([{"role": "user", "content": prompt}])


def continuar_conversa(
    pergunta_original: str,
    resposta_original: str,
    versiculos: list[dict],
    historico: list[dict],
    pergunta_nova: str,
) -> str:
    contexto = _montar_contexto(versiculos)

    instrucao = f"""Voce e um assistente que responde perguntas usando EXCLUSIVAMENTE os versiculos da Biblia fornecidos abaixo.
Nao use conhecimento proprio nem invente nada fora dos versiculos.
Se nenhum versiculo responder a pergunta, diga isso claramente.

Versiculos:
{contexto}"""

    messages = [
        {"role": "user", "content": instrucao},
        {"role": "user", "content": pergunta_original},
        {"role": "assistant", "content": resposta_original},
        *historico,
        {"role": "user", "content": pergunta_nova},
    ]

    return _chamar_chat(messages)
