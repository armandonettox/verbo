import json
from datetime import date

EPOCA = date(2026, 1, 1)


def carregar_capitulos_estruturados(caminho):
    """Le o JSON da Biblia e devolve a lista de capitulos, cada um com a lista
    de versiculos separada (usado pela API)."""
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)

    capitulos = []
    for testamento in ("antigoTestamento", "novoTestamento"):
        for livro in dados[testamento]:
            for capitulo in livro["capitulos"]:
                capitulos.append({
                    "livro": livro["nome"],
                    "capitulo": capitulo["capitulo"],
                    "versiculos": [
                        {"versiculo": v["versiculo"], "texto": v["texto"]}
                        for v in capitulo["versiculos"]
                    ],
                })
    return capitulos
