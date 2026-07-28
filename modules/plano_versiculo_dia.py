import json
from datetime import date

import streamlit as st

from config import BIBLE_JSON_PATH
from modules.leitura import EPOCA


@st.cache_data
def carregar_versiculos():
    with open(BIBLE_JSON_PATH, encoding="utf-8") as f:
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


def obter_versiculo_do_dia(data=None):
    if data is None:
        data = date.today()

    versiculos = carregar_versiculos()
    total = len(versiculos)
    idx = (data - EPOCA).days % total
    item = versiculos[idx]

    referencia = f"{item['livro']} {item['capitulo']},{item['versiculo']}"

    return {"referencia": referencia, "texto": item["texto"], "data": data}
