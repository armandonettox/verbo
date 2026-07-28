import streamlit as st


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


def _renderizar_lista_livros(livros, prefixo_key):
    colunas = st.columns(4)
    for posicao, livro in enumerate(livros):
        coluna = colunas[posicao % 4]
        with coluna:
            if st.button(livro["livro"], key=f"{prefixo_key}_{livro['indice_inicial']}", use_container_width=True):
                st.session_state.livro_selecionado = livro
                st.rerun()


def _renderizar_grade_capitulos(livro_selecionado, prefixo_key):
    colunas = st.columns(5)
    for numero in range(1, livro_selecionado["total_capitulos"] + 1):
        indice_absoluto = livro_selecionado["indice_inicial"] + (numero - 1)
        coluna = colunas[(numero - 1) % 5]
        with coluna:
            if st.button(str(numero), key=f"{prefixo_key}_{indice_absoluto}", use_container_width=True):
                st.session_state.capitulo_aberto = indice_absoluto
                st.rerun()
