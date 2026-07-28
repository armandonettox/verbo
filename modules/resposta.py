from openai import OpenAI
from config import NVIDIA_API_KEY, CHAT_MODEL

_client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1",
)


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

    resposta = _client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return resposta.choices[0].message.content


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

    resposta = _client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
    )

    return resposta.choices[0].message.content
