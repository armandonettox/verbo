from openai import OpenAI
from config import NVIDIA_API_KEY, CHAT_MODEL

_client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1",
)


def gerar_resposta(pergunta: str, versiculos: list[dict]) -> str:
    contexto = "\n".join(
        f"{v['referencia']}: {v['texto']}" for v in versiculos
    )

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
