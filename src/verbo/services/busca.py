from verbo.config import EMBEDDING_MODEL, SIMILARIDADE_MINIMA, TOP_K
from verbo.core.chroma_client import obter_colecao
from verbo.core.nvidia_client import obter_client_nvidia


def buscar_versiculos(pergunta: str) -> list[dict]:
    client = obter_client_nvidia()
    colecao = obter_colecao()

    resposta = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=pergunta,
        extra_body={"input_type": "query", "truncate": "END"},
    )
    vetor = resposta.data[0].embedding

    resultados = colecao.query(query_embeddings=[vetor], n_results=TOP_K)

    versiculos = []
    for texto, meta, distancia in zip(
        resultados["documents"][0], resultados["metadatas"][0], resultados["distances"][0]
    ):
        # colecao usa distancia L2 sobre embeddings normalizados, entao
        # equivale a similaridade de cosseno: cos = 1 - distancia/2
        similaridade = max(0.0, min(1.0, 1 - distancia / 2)) * 100
        # resultados vem ordenados por distancia crescente, entao o
        # primeiro abaixo do limiar garante que os seguintes tambem estao
        if similaridade < SIMILARIDADE_MINIMA:
            break
        versiculos.append({
            "texto": texto,
            "referencia": meta["referencia"],
            "similaridade": round(similaridade, 2),
        })

    return versiculos
