import json
from datetime import date

import streamlit as st

from config import BIBLE_JSON_PATH

EPOCA = date(2026, 1, 1)


@st.cache_data
def carregar_capitulos():
    with open(BIBLE_JSON_PATH, encoding="utf-8") as f:
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


def capitulo_do_dia(offset=0):
    capitulos = carregar_capitulos()
    total = len(capitulos)
    indice_dia = (date.today() - EPOCA).days + offset
    idx = indice_dia % total
    return idx, total, capitulos[idx]
