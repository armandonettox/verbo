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


def _renderizar_seletor_livro_capitulo(capitulos):
    livros = listar_livros(capitulos)
    livros_por_nome = {livro["livro"]: livro for livro in livros}
    nomes_livros = [livro["livro"] for livro in livros]

    idx_aberto = st.session_state.get("capitulo_aberto")
    if idx_aberto is None:
        idx_aberto = 0

    livro_atual = next(
        (l for l in livros if l["indice_inicial"] <= idx_aberto < l["indice_inicial"] + l["total_capitulos"]),
        livros[0],
    )
    st.session_state.sel_livro = livro_atual["livro"]
    st.session_state.sel_capitulo = idx_aberto - livro_atual["indice_inicial"] + 1

    def _livro_alterado():
        livro = livros_por_nome[st.session_state.sel_livro]
        st.session_state.capitulo_aberto = livro["indice_inicial"]

    def _capitulo_alterado():
        livro = livros_por_nome[st.session_state.sel_livro]
        st.session_state.capitulo_aberto = livro["indice_inicial"] + (st.session_state.sel_capitulo - 1)

    st.selectbox("Livro", nomes_livros, key="sel_livro", on_change=_livro_alterado)

    livro_selecionado = livros_por_nome[st.session_state.sel_livro]
    st.selectbox(
        "Capitulo",
        list(range(1, livro_selecionado["total_capitulos"] + 1)),
        key="sel_capitulo",
        on_change=_capitulo_alterado,
    )
