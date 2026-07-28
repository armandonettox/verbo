import json
import math
import re
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


def total_semanas(total_capitulos):
    return math.ceil(total_capitulos / 7)


def dias_na_semana(semana, total_capitulos):
    inicio = (semana - 1) * 7
    fim = min(inicio + 7, total_capitulos)
    return fim - inicio


def semana_dia_de_indice(idx):
    return idx // 7 + 1, idx % 7 + 1


def indice_de_semana_dia(semana, dia):
    return (semana - 1) * 7 + (dia - 1)


def texto_para_audio(capitulo):
    versiculos = re.split(r"\*\*\d+\.\*\*\s*", capitulo["texto"])
    versiculos = [v.replace("\n", " ").strip() for v in versiculos if v.strip()]
    return " ".join(versiculos)
