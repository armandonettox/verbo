import threading

from verbo.config import LOCAL_EMBEDDING_MODEL, FASTEMBED_CACHE_DIR

_modelo = None
_trava = threading.Lock()


def _obter_modelo():
    global _modelo
    with _trava:
        return _carregar_modelo()


def _carregar_modelo():
    global _modelo
    if _modelo is None:
        from fastembed import TextEmbedding
        from fastembed.common.model_description import ModelSource, PoolingType

        # O fastembed nao traz o multilingual-e5-small na lista oficial,
        # entao registramos o ONNX publicado pelo proprio autor do modelo.
        try:
            TextEmbedding.add_custom_model(
                model=LOCAL_EMBEDDING_MODEL,
                pooling=PoolingType.MEAN,
                normalization=True,
                sources=ModelSource(hf=LOCAL_EMBEDDING_MODEL),
                dim=384,
                model_file="onnx/model.onnx",
            )
        except ValueError:
            # ja registrado numa chamada anterior
            pass
        _modelo = TextEmbedding(LOCAL_EMBEDDING_MODEL, cache_dir=FASTEMBED_CACHE_DIR)
    return _modelo


def gerar_embeddings(textos: list[str], tipo: str) -> list[list[float]]:
    """Gera embeddings locais. tipo e "query" (pergunta) ou "passage" (trecho
    da Biblia). O modelo e5 exige esse prefixo no texto para funcionar bem."""
    if tipo not in ("query", "passage"):
        raise ValueError("tipo deve ser 'query' ou 'passage'")
    prefixados = [f"{tipo}: {t}" for t in textos]
    return [vetor.tolist() for vetor in _obter_modelo().embed(prefixados)]
