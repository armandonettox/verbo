import streamlit as st

from modules.audio_widget import renderizar_audio
from modules.leitura import carregar_capitulos, texto_para_audio

TOTAL_LIVROS_ANTIGO_TESTAMENTO = 46


@st.cache_data
def listar_livros(capitulos):
    livros = []
    for idx, capitulo in enumerate(capitulos):
        if livros and livros[-1]["livro"] == capitulo["livro"]:
            livros[-1]["total_capitulos"] += 1
        else:
            livros.append({
                "livro": capitulo["livro"],
                "indice_inicial": idx,
                "total_capitulos": 1,
            })
    return livros


def _inicializar_estado():
    if "livre_indice" not in st.session_state:
        st.session_state.livre_indice = 0
    if "livre_sumario" not in st.session_state:
        st.session_state.livre_sumario = True


def _renderizar_lista_livros(livros, prefixo_key):
    colunas = st.columns(3)
    for posicao, livro in enumerate(livros):
        coluna = colunas[posicao % 3]
        with coluna:
            rotulo = f"{livro['livro']} ({livro['total_capitulos']} capitulos)"
            if st.button(rotulo, key=f"{prefixo_key}_{livro['indice_inicial']}", use_container_width=True):
                st.session_state.livro_selecionado = livro
                st.rerun()


def _renderizar_grade_capitulos(livro_selecionado, capitulos, prefixo_key):
    colunas = st.columns(5)
    for numero in range(1, livro_selecionado["total_capitulos"] + 1):
        indice_absoluto = livro_selecionado["indice_inicial"] + (numero - 1)
        coluna = colunas[(numero - 1) % 5]
        with coluna:
            if st.button(str(numero), key=f"{prefixo_key}_{indice_absoluto}", use_container_width=True):
                st.session_state.capitulo_aberto = indice_absoluto
                st.rerun()


def _renderizar_sumario(capitulos):
    livros = listar_livros(capitulos)
    livros_antigo = livros[:TOTAL_LIVROS_ANTIGO_TESTAMENTO]
    livros_novo = livros[TOTAL_LIVROS_ANTIGO_TESTAMENTO:]

    with st.sidebar:
        st.caption("Escolha um livro para comecar")

    st.markdown("### Sumario")

    st.markdown("**Antigo Testamento**")
    _renderizar_lista_livros(livros_antigo, "livro_at")

    st.markdown("**Novo Testamento**")
    _renderizar_lista_livros(livros_novo, "livro_nt")


def _renderizar_leitura(capitulos, cor_fundo, cor_texto, cor_mutado, cor_destaque):
    capitulo = capitulos[st.session_state.livre_indice]

    with st.sidebar:
        with st.container(border=True, key="sb_livre_posicao"):
            st.caption(f"{capitulo['livro']} {capitulo['capitulo']}")
            if st.button("Sumario", use_container_width=True, key="livre_btn_sumario"):
                st.session_state.livre_sumario = True
                st.rerun()

    st.markdown(f"### {capitulo['livro']} {capitulo['capitulo']}")
    st.markdown(capitulo["texto"])

    renderizar_audio(
        texto_para_audio(capitulo),
        key="sb_audio_livre",
        cor_fundo=cor_fundo,
        cor_texto=cor_texto,
        cor_mutado=cor_mutado,
        cor_destaque=cor_destaque,
        rotulo="Ouvir capitulo",
    )

    col_anterior, col_proximo = st.columns(2)
    with col_anterior:
        if st.button("Capitulo Anterior", use_container_width=True, key="livre_btn_anterior"):
            st.session_state.livre_indice = max(0, st.session_state.livre_indice - 1)
            st.rerun()
    with col_proximo:
        if st.button("Proximo Capitulo", use_container_width=True, key="livre_btn_proximo"):
            st.session_state.livre_indice = min(len(capitulos) - 1, st.session_state.livre_indice + 1)
            st.rerun()


def renderizar(cor_fundo, cor_texto, cor_mutado, cor_destaque):
    _inicializar_estado()

    capitulos = carregar_capitulos()

    if st.session_state.livre_sumario:
        _renderizar_sumario(capitulos)
    else:
        _renderizar_leitura(capitulos, cor_fundo, cor_texto, cor_mutado, cor_destaque)
