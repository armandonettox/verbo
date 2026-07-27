import streamlit as st
from modules.busca import buscar_versiculos
from modules.resposta import gerar_resposta
from modules.leitura import (
    capitulo_do_dia, carregar_capitulos, carregar_capitulos_busca, sem_acento,
    total_semanas, dias_na_semana, semana_dia_de_indice, indice_de_semana_dia,
)

st.set_page_config(page_title="Verbo", page_icon="assets/favicon.png", layout="centered")

if "tema_escuro" not in st.session_state:
    st.session_state.tema_escuro = False

if st.session_state.tema_escuro:
    cor_fundo, cor_fundo_2, cor_texto, cor_mutado, cor_borda = (
        "#221A12", "#33281B", "#F1E8D8", "#C9B79E", "#4A3B28"
    )
else:
    cor_fundo, cor_fundo_2, cor_texto, cor_mutado, cor_borda = (
        "#FBF6EC", "#F1E8D8", "#3B2A1E", "#6B4F3A", "#F1E8D8"
    )
cor_destaque = "#B8860B"

st.markdown(
    f"""
    <style>
    [data-testid="stHeader"] {{ display: none; }}
    [data-testid="stToolbar"] {{ display: none; }}
    [data-testid="stBottom"] {{ display: none; }}
    .st-key-logo_center [data-testid="StyledFullScreenButton"] {{ display: none; }}
    .st-key-logo_center [data-testid="stElementToolbar"] {{ display: none; }}
    [data-testid="stMain"] {{ padding-top: 0 !important; }}
    [data-testid="stAppViewContainer"] {{ padding-top: 0 !important; }}
    .block-container {{ padding-top: 0 !important; padding-bottom: 1rem !important; }}

    [data-testid="stAppViewContainer"] {{ background-color: {cor_fundo}; }}
    [data-testid="stSidebar"] {{ background-color: {cor_fundo_2}; }}
    [data-testid="stSidebar"] * {{ color: {cor_texto}; }}
    h1, h2, h3, h4, p, span, label, li {{ color: {cor_texto}; }}
    .stTextInput input, .stNumberInput input, [data-baseweb="select"] > div {{
        background-color: {cor_fundo_2} !important;
        color: {cor_texto} !important;
    }}
    .stButton button, .stFormSubmitButton button {{
        background-color: {cor_fundo};
        color: {cor_texto};
        border: 1px solid {cor_mutado};
    }}

    .bloco-central {{ text-align: center; margin-bottom: 1.5rem; }}
    .bloco-central h1 {{ font-size: 2.75rem; margin-bottom: 0.5rem; }}
    .bloco-central p {{ color: {cor_mutado} !important; font-style: italic; font-size: 1.05rem; }}

    .barra-topo {{ display: flex; align-items: center; gap: 0.5rem; height: 100%; }}
    .barra-topo a {{ color: {cor_mutado}; }}
    .barra-topo a:hover {{ color: {cor_destaque}; }}

    .st-key-barra_menu {{
        width: 100vw;
        max-width: 100vw;
        margin-left: calc(-50vw + 50%);
        margin-right: calc(-50vw + 50%);
        margin-bottom: 2rem;
        padding: 0.75rem 1.5rem 1rem;
        box-sizing: border-box;
        border-bottom: 1px solid {cor_mutado};
    }}

    .st-key-logo_center {{ display: flex; justify-content: center; align-items: center; height: 100%; }}
    .st-key-logo_center img {{
        background-color: #FBF6EC;
        padding: 0.35rem;
        border-radius: 0.4rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container(key="barra_menu"):
    col_nav, col_logo, col_git, col_tema = st.columns([1.4, 2, 0.6, 0.8])
    with col_nav:
        pagina = st.segmented_control(
            "Navegacao",
            ["Busca Semantica", "Plano de Leitura"],
            default="Busca Semantica",
            label_visibility="collapsed",
            key="nav",
            format_func=lambda opcao: (
                ":material/search: Busca Semantica"
                if opcao == "Busca Semantica"
                else ":material/menu_book: Plano de Leitura"
            ),
        )
    with col_logo:
        with st.container(key="logo_center"):
            st.image("assets/logo.png", width=44)
    with col_git:
        st.markdown(
            '<div class="barra-topo">'
            '<a href="https://github.com/armandonettox/verbo" target="_blank" title="Ver codigo no GitHub">'
            '<svg height="22" viewBox="0 0 16 16" width="22" fill="currentColor">'
            '<path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 '
            '0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 '
            '1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 '
            '0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 '
            '1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 '
            '3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z">'
            '</path></svg></a></div>',
            unsafe_allow_html=True,
        )
    with col_tema:
        icone_tema = ":material/dark_mode:" if not st.session_state.tema_escuro else ":material/light_mode:"
        if st.button(icone_tema, key="botao_tema", use_container_width=True):
            st.session_state.tema_escuro = not st.session_state.tema_escuro
            st.rerun()

st.markdown('<div class="bloco-central">', unsafe_allow_html=True)
st.markdown("# Explore as Escrituras")
st.markdown(
    "*Pesquise e descubra passagens biblicas com compreensao semantica "
    "e insights contextuais.*"
)
st.markdown("</div>", unsafe_allow_html=True)

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
    f"""
    <hr style="margin-top: 3rem; border-color: {cor_mutado}; width: 100vw; max-width: 100vw; margin-left: calc(-50vw + 50%); margin-right: calc(-50vw + 50%);">
    <p style="text-align: center; color: {cor_mutado}; font-size: 0.85rem;">
        Feito por armandonettox &middot; texto: Biblia Catolica Ave Maria
    </p>
    """,
    unsafe_allow_html=True,
)
