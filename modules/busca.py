import chromadb
from openai import OpenAI
from config import (
    NVIDIA_API_KEY, CHROMA_DB_PATH, COLLECTION_NAME,
    EMBEDDING_MODEL, TOP_K
)

_client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1",
)
_chroma = chromadb.PersistentClient(path=CHROMA_DB_PATH)
_colecao = _chroma.get_collection(COLLECTION_NAME)


def buscar_versiculos(pergunta: str) -> list[dict]:
    resposta = _client.embeddings.create(model=EMBEDDING_MODEL, input=pergunta)
    vetor = resposta.data[0].embedding

    resultados = _colecao.query(query_embeddings=[vetor], n_results=TOP_K)

    versiculos = []
    for texto, meta in zip(resultados["documents"][0], resultados["metadatas"][0]):
        versiculos.append({"texto": texto, "referencia": meta["referencia"]})

    return versiculos
