import logging
import time

import chromadb
import chromadb.errors
import openai
from openai import OpenAI
from verbo.config import (
    NVIDIA_API_KEY, CHROMA_DB_PATH, COLLECTION_NAME, COLLECTION_NAME_LOCAL,
    EMBEDDING_MODEL, TOP_K, TOP_K_LOCAL, SIMILARIDADE_MINIMA,
    BUSCA_TIMEOUT_SEGUNDOS, DISJUNTOR_FALHAS, DISJUNTOR_PAUSA_SEGUNDOS
)
from verbo.core import metricas
from verbo.core.disjuntor import Disjuntor
from verbo.core.embedding_local import gerar_embeddings

logger = logging.getLogger(__name__)

# Falhas da NVIDIA (ou do indice dela) que levam ao fallback local
_ERROS_QUE_ACIONAM_FALLBACK = (openai.OpenAIError, chromadb.errors.ChromaError)

_client = None
_colecoes = {}
disjuntor = Disjuntor(DISJUNTOR_FALHAS, DISJUNTOR_PAUSA_SEGUNDOS)


def _obter_client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=NVIDIA_API_KEY,
            base_url="https://integrate.api.nvidia.com/v1",
            timeout=BUSCA_TIMEOUT_SEGUNDOS,
            max_retries=0,
        )
    return _client


def _obter_colecao(nome):
    if nome not in _colecoes:
        chroma = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        _colecoes[nome] = chroma.get_collection(nome)
    return _colecoes[nome]


def _similaridade(distancia):
    # colecao usa distancia L2 sobre embeddings normalizados, entao
    # equivale a similaridade de cosseno: cos = 1 - distancia/2
    return max(0.0, min(1.0, 1 - distancia / 2)) * 100


def _formatar(resultados, similaridade_minima=None):
    versiculos = []
    for texto, meta, distancia in zip(
        resultados["documents"][0], resultados["metadatas"][0], resultados["distances"][0]
    ):
        similaridade = _similaridade(distancia)
        # resultados vem ordenados por distancia crescente, entao o
        # primeiro abaixo do limiar garante que os seguintes tambem estao
        if similaridade_minima is not None and similaridade < similaridade_minima:
            break
        versiculos.append({
            "texto": texto,
            "referencia": meta["referencia"],
            "similaridade": round(similaridade, 2),
        })
    return versiculos


def buscar_versiculos(pergunta: str) -> list[dict]:
    """Busca pelo indice da NVIDIA. Levanta excecao se a NVIDIA falhar."""
    resposta = _obter_client().embeddings.create(
        model=EMBEDDING_MODEL,
        input=pergunta,
        extra_body={"input_type": "query", "truncate": "END"},
    )
    vetor = resposta.data[0].embedding

    resultados = _obter_colecao(COLLECTION_NAME).query(
        query_embeddings=[vetor], n_results=TOP_K
    )
    return _formatar(resultados, SIMILARIDADE_MINIMA)


def buscar_versiculos_local(pergunta: str) -> list[dict]:
    """Busca pelo indice local (fallback). O modelo e5 da notas muito proximas
    entre si, entao nao usa corte de similaridade: devolve os TOP_K_LOCAL
    mais proximos."""
    vetor = gerar_embeddings([pergunta], "query")[0]
    resultados = _obter_colecao(COLLECTION_NAME_LOCAL).query(
        query_embeddings=[vetor], n_results=TOP_K_LOCAL
    )
    versiculos = _formatar(resultados)
    # a nota do e5 e quase igual para tudo (81 a 87), entao nao e mostrada
    for v in versiculos:
        v["similaridade"] = None
    return versiculos


def _buscar_local_com_metricas(pergunta):
    inicio = time.monotonic()
    versiculos = buscar_versiculos_local(pergunta)
    metricas.registrar_latencia("busca_local", time.monotonic() - inicio)
    return versiculos


def buscar_com_fallback(pergunta: str) -> dict:
    """Tenta a NVIDIA e, se ela falhar, cai para a busca local.
    Retorna {"versiculos": [...], "modo": "nvidia" | "local"}."""
    if not disjuntor.permite():
        metricas.contar("busca_disjuntor_aberto")
        return {"versiculos": _buscar_local_com_metricas(pergunta), "modo": "local"}

    inicio = time.monotonic()
    try:
        versiculos = buscar_versiculos(pergunta)
    except _ERROS_QUE_ACIONAM_FALLBACK as erro:
        disjuntor.registrar_falha()
        metricas.contar("busca_fallback")
        logger.warning("Busca NVIDIA falhou (%s), usando busca local", type(erro).__name__)
        return {"versiculos": _buscar_local_com_metricas(pergunta), "modo": "local"}

    disjuntor.registrar_sucesso()
    metricas.registrar_latencia("busca_nvidia", time.monotonic() - inicio)
    return {"versiculos": versiculos, "modo": "nvidia"}
