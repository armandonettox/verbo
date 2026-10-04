import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RAIZ))
sys.path.insert(0, str(_RAIZ / "src"))


import pytest


@pytest.fixture(autouse=True)
def _zerar_estado_global():
    # disjuntores e metricas sao globais do processo; cada teste comeca limpo
    from verbo.core import busca, metricas, resposta

    for disjuntor in (busca.disjuntor, resposta.disjuntor):
        disjuntor.registrar_sucesso()
    metricas.zerar()
    busca._embeddings_recentes.clear()
    yield
