import json
from datetime import date

import streamlit as st

from config import BIBLE_JSON_PATH
from modules.leitura import EPOCA
from modules.audio_widget import renderizar_audio

MESES = [
    "janeiro", "fevereiro", "marco", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


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


def data_por_extenso(data):
    return f"{data.day} de {MESES[data.month - 1]} de {data.year}"


def renderizar(cor_fundo, cor_texto, cor_mutado, cor_destaque):
    versiculos = carregar_versiculos()
    total = len(versiculos)
    idx = (date.today() - EPOCA).days % total
    item = versiculos[idx]

    referencia = f"{item['livro']} {item['capitulo']},{item['versiculo']}"

    with st.container(key="versiculo_dia"):
        st.caption(data_por_extenso(date.today()))
        st.subheader(referencia)
        st.markdown(
            f'<p style="font-size:1.3rem; font-style:italic;">{item["texto"]}</p>',
            unsafe_allow_html=True,
        )
        renderizar_audio(
            item["texto"],
            key="sb_audio_dia",
            cor_fundo=cor_fundo,
            cor_texto=cor_texto,
            cor_mutado=cor_mutado,
            cor_destaque=cor_destaque,
            rotulo="Ouvir versiculo",
        )
