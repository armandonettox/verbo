import json
from datetime import date

from verbo.core.leitura import EPOCA


def carregar_versiculos_do_arquivo(caminho):
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)

    versiculos = []
    for testamento in ("antigoTestamento", "novoTestamento"):
        for livro in dados[testamento]:
            for capitulo in livro["capitulos"]:
                for versiculo in capitulo["versiculos"]:
                    versiculos.append({
                        "livro": livro["nome"],
                        "capitulo": capitulo["capitulo"],
                        "versiculo": versiculo["versiculo"],
                        "texto": versiculo["texto"],
                    })
    return versiculos


def obter_versiculo_do_dia(versiculos, data=None):
    if data is None:
        data = date.today()

    total = len(versiculos)
    idx = (data - EPOCA).days % total
    item = versiculos[idx]

    referencia = f"{item['livro']} {item['capitulo']},{item['versiculo']}"

    return {"referencia": referencia, "texto": item["texto"], "data": data}
