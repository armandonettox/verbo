import streamlit as st
from modules.busca import buscar_versiculos
from modules.resposta import gerar_resposta
from modules.leitura import capitulo_do_dia

st.set_page_config(page_title="Verbo", page_icon="assets/favicon.png", layout="centered")

st.markdown(
    """
    <style>
    [data-testid="stHeader"] { display: none; }
    [data-testid="stToolbar"] { display: none; }
    .block-container { padding-top: 2.5rem; }
    .bloco-central { text-align: center; margin-bottom: 1.5rem; }
    .bloco-central .marca { font-size: 1.1rem; color: #6B4F3A; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.5rem; }
    .bloco-central h1 { font-size: 2.75rem; margin-bottom: 0.5rem; }
    .bloco-central p { color: #6B4F3A; font-style: italic; font-size: 1.05rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="bloco-central">', unsafe_allow_html=True)
st.image("assets/logo.png", width=100)
st.markdown('<p class="marca">Verbo</p>', unsafe_allow_html=True)
st.markdown("# Explore as Escrituras")
st.markdown(
    "*Pesquise e descubra passagens biblicas com compreensao semantica "
    "e insights contextuais.*"
)
st.markdown("</div>", unsafe_allow_html=True)

aba_busca, aba_leitura = st.tabs(["Busca Semantica", "Plano de Leitura"])

with aba_busca:
    with st.form("busca_form"):
        col_campo, col_botao = st.columns([5, 1])
        with col_campo:
            pergunta = st.text_input(
                "Qual e a sua pergunta?",
                label_visibility="collapsed",
                placeholder="O que Jesus disse sobre o amor ao proximo?",
            )
        with col_botao:
            enviar = st.form_submit_button("Buscar", use_container_width=True)

    if enviar and pergunta:
        with st.spinner("Buscando versiculos..."):
            versiculos = buscar_versiculos(pergunta)

        with st.spinner("Gerando resposta..."):
            resposta = gerar_resposta(pergunta, versiculos)

        st.markdown("### Resposta")
        st.write(resposta)

        st.markdown("### Versiculos consultados")
        for v in versiculos:
            st.markdown(f"**{v['referencia']}** — {v['texto']}")

with aba_leitura:
    if "offset_leitura" not in st.session_state:
        st.session_state.offset_leitura = 0

    idx, total, capitulo = capitulo_do_dia(st.session_state.offset_leitura)

    st.caption(f"Dia {idx + 1} de {total} — um capitulo por dia")
    st.markdown(f"### {capitulo['livro']} {capitulo['capitulo']}")
    st.markdown(capitulo["texto"])

    col_anterior, col_hoje, col_proximo = st.columns(3)
    with col_anterior:
        if st.button("Anterior", use_container_width=True):
            st.session_state.offset_leitura -= 1
            st.rerun()
    with col_hoje:
        if st.button("Hoje", use_container_width=True):
            st.session_state.offset_leitura = 0
            st.rerun()
    with col_proximo:
        if st.button("Proximo", use_container_width=True):
            st.session_state.offset_leitura += 1
            st.rerun()

st.markdown(
    """
    <hr style="margin-top: 3rem; border-color: #F1E8D8;">
    <p style="text-align: center; color: #6B4F3A; font-size: 0.85rem;">
        Feito por armandonettox &middot; texto: Biblia Catolica Ave Maria
    </p>
    """,
    unsafe_allow_html=True,
)
