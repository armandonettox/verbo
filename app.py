import streamlit as st
from modules.busca import buscar_versiculos
from modules.resposta import gerar_resposta
from modules.leitura import (
    capitulo_do_dia, carregar_capitulos, carregar_capitulos_busca, sem_acento,
    total_semanas, dias_na_semana, semana_dia_de_indice, indice_de_semana_dia,
)

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

pagina = st.segmented_control(
    "Navegacao",
    ["Busca Semantica", "Plano de Leitura"],
    default="Busca Semantica",
    label_visibility="collapsed",
    key="nav",
)

if pagina == "Busca Semantica":
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

else:
    if "offset_leitura" not in st.session_state:
        st.session_state.offset_leitura = 0
    if "auto_hoje" not in st.session_state:
        st.session_state.auto_hoje = True
    if "dias_concluidos" not in st.session_state:
        st.session_state.dias_concluidos = set()

    idx_hoje, total, _ = capitulo_do_dia(0)

    if st.session_state.auto_hoje:
        st.session_state.offset_leitura = 0

    idx, total, capitulo = capitulo_do_dia(st.session_state.offset_leitura)
    semana_atual, dia_atual = semana_dia_de_indice(idx)

    with st.sidebar:
        with st.container(border=True):
            st.caption("PLANO DE LEITURA")
            st.selectbox("Plano", ["Sequencial - 1 capitulo/dia"], disabled=True)
            st.markdown("**Biblia Ave Maria - ordem canonica**")
            st.caption(
                "Um capitulo por dia, do Genesis ao Apocalipse, seguindo a "
                "ordem dos livros da Biblia Catolica Ave Maria (nao e um "
                "plano cronologico)."
            )

        with st.container(border=True):
            n_semanas = total_semanas(total)
            col_sem, col_dia = st.columns(2)
            with col_sem:
                semana_sel = st.selectbox(
                    "Semana", list(range(1, n_semanas + 1)),
                    index=semana_atual - 1, disabled=st.session_state.auto_hoje,
                )
            with col_dia:
                n_dias = dias_na_semana(semana_sel, total)
                dia_sel = st.selectbox(
                    "Dia", list(range(1, n_dias + 1)),
                    index=min(dia_atual, n_dias) - 1, disabled=st.session_state.auto_hoje,
                )

            col_hoje, col_auto = st.columns(2)
            with col_hoje:
                if st.button("Hoje", use_container_width=True):
                    st.session_state.auto_hoje = True
                    st.session_state.offset_leitura = 0
                    st.rerun()
            with col_auto:
                auto = st.checkbox("Auto hoje", value=st.session_state.auto_hoje)
                if auto != st.session_state.auto_hoje:
                    st.session_state.auto_hoje = auto
                    st.rerun()

            if not st.session_state.auto_hoje:
                novo_idx = indice_de_semana_dia(semana_sel, dia_sel)
                novo_offset = novo_idx - idx_hoje
                if novo_offset != st.session_state.offset_leitura:
                    st.session_state.offset_leitura = novo_offset
                    st.rerun()

        with st.container(border=True):
            st.text_input(
                "Leitura atual",
                value=f"{capitulo['livro']} {capitulo['capitulo']}",
                disabled=True,
                label_visibility="collapsed",
            )

            concluido = idx in st.session_state.dias_concluidos
            rotulo = "Concluido nesta sessao" if concluido else "Marcar como concluido"
            if st.button(rotulo, use_container_width=True):
                if concluido:
                    st.session_state.dias_concluidos.discard(idx)
                else:
                    st.session_state.dias_concluidos.add(idx)
                st.rerun()
            st.caption("Progresso salvo so nesta sessao — some ao recarregar a pagina.")

            st.checkbox("Audio (em breve)", disabled=True)
            st.checkbox("Comentarios dos Padres da Igreja (em breve)", disabled=True)

            palavra_chave = st.text_input("Buscar palavra-chave", placeholder="ex: misericordia")
            if palavra_chave:
                capitulos_todos = carregar_capitulos()
                textos_normalizados = carregar_capitulos_busca()
                termo = sem_acento(palavra_chave)
                achou = False
                for i, texto_norm in enumerate(textos_normalizados):
                    if termo in texto_norm:
                        achou = True
                        c = capitulos_todos[i]
                        st.caption(f"Encontrado em {c['livro']} {c['capitulo']}")
                        if st.button(f"Ir para {c['livro']} {c['capitulo']}", key=f"ir_{i}"):
                            st.session_state.auto_hoje = False
                            st.session_state.offset_leitura = i - idx_hoje
                            st.rerun()
                        break
                if not achou:
                    st.caption("Nenhum capitulo encontrado.")

            if st.button("Tentar Busca Semantica", use_container_width=True):
                st.session_state.nav = "Busca Semantica"
                st.rerun()

        with st.container(border=True):
            st.markdown("**Progresso**")
            st.progress((idx + 1) / total)
            st.caption(f"{idx + 1} / {total} dias ({total - idx - 1} faltam)")

    st.caption(f"Dia {idx + 1} de {total}")
    st.markdown(f"### {capitulo['livro']} {capitulo['capitulo']}")
    st.markdown(capitulo["texto"])

    col_anterior, col_proximo = st.columns(2)
    with col_anterior:
        if st.button("Anterior", use_container_width=True):
            st.session_state.auto_hoje = False
            st.session_state.offset_leitura -= 1
            st.rerun()
    with col_proximo:
        if st.button("Proximo", use_container_width=True):
            st.session_state.auto_hoje = False
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
