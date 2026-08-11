import streamlit as st

from verbo.config import BIBLE_JSON_PATH
from verbo.core.leitura import carregar_capitulos_do_arquivo
from verbo.core.versiculo_dia import carregar_versiculos_do_arquivo


@st.cache_data
def carregar_capitulos():
    return carregar_capitulos_do_arquivo(BIBLE_JSON_PATH)


@st.cache_data
def carregar_versiculos():
    return carregar_versiculos_do_arquivo(BIBLE_JSON_PATH)
