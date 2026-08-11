import streamlit as st

from verbo.core.plano_livre import listar_livros


def renderizar_seletor_livro_capitulo(capitulos):
    livros = listar_livros(capitulos)
    livros_por_nome = {livro["livro"]: livro for livro in livros}
    nomes_livros = [livro["livro"] for livro in livros]

    if "sel_livro" not in st.session_state:
        idx_aberto = st.session_state.get("capitulo_aberto") or 0
        livro_atual = next(
            (l for l in livros if l["indice_inicial"] <= idx_aberto < l["indice_inicial"] + l["total_capitulos"]),
            livros[0],
        )
        st.session_state.sel_livro = livro_atual["livro"]
        st.session_state.sel_capitulo = idx_aberto - livro_atual["indice_inicial"] + 1

    def _livro_alterado():
        st.session_state.sel_capitulo = 1

    st.selectbox("Livro", nomes_livros, key="sel_livro", on_change=_livro_alterado)

    livro_selecionado = livros_por_nome[st.session_state.sel_livro]
    st.selectbox(
        "Capitulo",
        list(range(1, livro_selecionado["total_capitulos"] + 1)),
        key="sel_capitulo",
    )

    if st.button("Comecar leitura", use_container_width=True, key="btn_comecar_leitura"):
        st.session_state.capitulo_aberto = livro_selecionado["indice_inicial"] + (st.session_state.sel_capitulo - 1)
        st.rerun()
