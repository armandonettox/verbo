import streamlit as st
from modules.busca import buscar_versiculos
from modules.resposta import gerar_resposta

st.set_page_config(page_title="Verbo", page_icon="assets/favicon.png")

st.image("assets/logo.png", width=150)
st.title("Verbo")
st.caption("Respostas baseadas exclusivamente na Biblia Catolica Ave Maria")

pergunta = st.text_input("Qual e a sua pergunta?")

if pergunta:
    with st.spinner("Buscando versiculos..."):
        versiculos = buscar_versiculos(pergunta)

    with st.spinner("Gerando resposta..."):
        resposta = gerar_resposta(pergunta, versiculos)

    st.markdown("### Resposta")
    st.write(resposta)

    st.markdown("### Versiculos consultados")
    for v in versiculos:
        st.markdown(f"**{v['referencia']}** — {v['texto']}")
