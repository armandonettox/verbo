import json
import re
from datetime import date

EPOCA = date(2026, 1, 1)


def carregar_capitulos_do_arquivo(caminho):
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)

    capitulos = []
    for testamento in ("antigoTestamento", "novoTestamento"):
        for livro in dados[testamento]:
            for capitulo in livro["capitulos"]:
                texto = "\n\n".join(
                    f"**{v['versiculo']}.** {v['texto']}" for v in capitulo["versiculos"]
                )
                capitulos.append({
                    "livro": livro["nome"],
                    "capitulo": capitulo["capitulo"],
                    "texto": texto,
                })
    return capitulos


def texto_para_audio(capitulo):
    versiculos = re.split(r"\*\*\d+\.\*\*\s*", capitulo["texto"])
    versiculos = [v.replace("\n", " ").strip() for v in versiculos if v.strip()]
    return " ".join(versiculos)
