import json

import streamlit as st
import streamlit.components.v1 as components
from modules.busca import buscar_versiculos
from modules.resposta import gerar_resposta
from modules.leitura import (
    capitulo_do_dia, total_semanas, dias_na_semana,
    semana_dia_de_indice, indice_de_semana_dia, texto_para_audio,
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
    [data-testid="stHeader"] {{
        background: transparent !important;
        box-shadow: none !important;
        height: 0 !important;
        min-height: 0 !important;
    }}
    [data-testid="stToolbarActions"] {{ display: none !important; }}
    [data-testid="stMainMenu"] {{ display: none !important; }}
    [data-testid="stAppDeployButton"] {{ display: none !important; }}
    [data-testid="stExpandSidebarButton"] {{ z-index: 999999 !important; }}
    [data-testid="stBottom"] {{ display: none; }}
    .st-key-logo_center [data-testid="StyledFullScreenButton"] {{ display: none; }}
    .st-key-logo_center [data-testid="stElementToolbar"] {{ display: none; }}
    [data-testid="stMain"] {{ padding-top: 0 !important; }}
    [data-testid="stAppViewContainer"] {{ padding-top: 0 !important; }}
    .block-container {{
        padding-top: 5.5rem !important;
        padding-bottom: 1rem !important;
        min-height: 100vh !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
    }}
    [data-testid="stLayoutWrapper"]:has(> .st-key-rodape_pagina) {{
        margin-top: auto;
    }}

    [data-testid="stAppViewContainer"] {{ background-color: {cor_fundo}; }}
    [data-testid="stSidebar"] {{ background-color: {cor_fundo}; }}
    [data-testid="stSidebar"][aria-expanded="true"] {{
        width: 380px !important;
        min-width: 380px !important;
        max-width: 380px !important;
    }}
    [data-testid="stSidebar"] div[style*="cursor: col-resize"] {{
        display: none !important;
        pointer-events: none !important;
    }}
    [data-testid="stSidebar"] * {{ color: {cor_texto}; }}

    [data-testid="stSidebarUserContent"] {{ padding-top: 0.4rem !important; }}
    [data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] {{
        gap: 0.25rem !important;
    }}
    .st-key-sb_plano, .st-key-sb_semana_dia, .st-key-sb_leitura_atual, .st-key-sb_progresso {{
        padding: 0.4rem !important;
        gap: 0.2rem !important;
    }}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
        font-size: 0.7rem !important;
        line-height: 1.25 !important;
    }}
    [data-testid="stSidebar"] .stButton button,
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        min-height: 1.6rem !important;
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
    }}
    [data-testid="stSidebar"] .stButton button p,
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] [data-baseweb="select"] * {{
        font-size: 0.76rem !important;
    }}
    [data-testid="stSidebar"] .stCheckbox {{ min-height: 1.2rem !important; }}
    [data-testid="stSidebar"] .stWidgetLabel {{ margin-bottom: 0.1rem !important; }}
    [data-testid="stSidebar"] .stWidgetLabel p {{ font-size: 0.76rem !important; }}
    [data-testid="stSidebar"] .stProgress {{ margin: 0 !important; }}
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {{ gap: 0.4rem !important; }}
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

    .st-key-botao_tema {{ display: flex; align-items: center; height: 100%; }}
    .st-key-botao_tema button {{
        background-color: transparent;
        border: none;
        box-shadow: none;
        color: {cor_mutado};
        padding: 0;
    }}
    .st-key-botao_tema button:hover {{
        color: {cor_destaque};
        background-color: transparent;
    }}
    .st-key-botao_tema span[role="img"] {{ font-size: 22px !important; }}

    .bloco-central {{ text-align: center; margin-bottom: 1.5rem; }}
    .bloco-central h1 {{ font-size: 2.75rem; margin-bottom: 0.5rem; }}
    .bloco-central p {{ color: {cor_mutado} !important; font-style: italic; font-size: 1.05rem; }}

    .barra-topo {{ display: flex; align-items: center; gap: 0.5rem; height: 100%; }}
    .barra-topo a {{ color: {cor_mutado}; }}
    .barra-topo a:hover {{ color: {cor_destaque}; }}

    .st-key-barra_menu {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000000;
        padding: 0.75rem 1.5rem 1rem;
        box-sizing: border-box;
        background-color: {cor_fundo};
        border-bottom: 1px solid {cor_mutado};
    }}

    .st-key-logo_center {{ display: flex; justify-content: center; align-items: center; height: 100%; }}
    .st-key-logo_center img {{
        background-color: #FBF6EC;
        padding: 0.35rem;
        border-radius: 0.4rem;
    }}

    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"] {{
        display: none !important;
    }}
    #slot-sidebar-toggle {{ display: flex; align-items: center; height: 100%; }}
    #slot-sidebar-toggle [data-testid="stSidebarCollapseButton"],
    #slot-sidebar-toggle [data-testid="stExpandSidebarButton"] {{
        display: flex !important;
        position: static !important;
        opacity: 1 !important;
        visibility: visible !important;
    }}
    #slot-sidebar-toggle button svg {{
        color: {cor_mutado} !important;
        width: 20px !important;
        height: 20px !important;
    }}

    div[data-testid="stElementContainer"]:has(> iframe) {{
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
        line-height: 0 !important;
    }}
    .st-key-sb_audio div[data-testid="stElementContainer"]:has(> iframe) {{
        height: 40px !important;
        min-height: 40px !important;
        line-height: normal !important;
    }}
    .st-key-sb_audio iframe {{ height: 40px !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

components.html(
    """
    <script>
    (function() {
        var doc = window.parent.document;
        function moverBotaoSidebar() {
            var slot = doc.getElementById('slot-sidebar-toggle');
            if (!slot) return;
            var btn = doc.querySelector('[data-testid="stSidebarCollapseButton"]')
                || doc.querySelector('[data-testid="stExpandSidebarButton"]');
            if (btn && btn.parentElement !== slot) {
                slot.appendChild(btn);
            }
        }
        moverBotaoSidebar();
        var obs = new MutationObserver(function() {
            try { moverBotaoSidebar(); } catch (e) {}
        });
        obs.observe(doc.body, {childList: true, subtree: true});
    })();
    </script>
    """,
    height=0,
)

with st.container(key="barra_menu"):
    col_nav, col_logo, col_espaco, col_acoes = st.columns([1.8, 2, 0.2, 1.6])
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
    with col_acoes:
        col_sidebar, col_git, col_tema = st.columns([1, 1, 1], gap="small")
        with col_sidebar:
            if pagina == "Plano de Leitura":
                st.markdown('<div id="slot-sidebar-toggle"></div>', unsafe_allow_html=True)
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
            if st.button(icone_tema, key="botao_tema"):
                st.session_state.tema_escuro = not st.session_state.tema_escuro
                st.rerun()

components.html(
    """
    <script>
    (function() {
        var doc = window.parent.document;
        var win = window.parent;
        var mostrar = MOSTRAR_FLAG;

        if (!win.__rolarAutomatico) {
            win.__rolarAutomatico = { rolando: false, intervalo: null };
        }
        var estado = win.__rolarAutomatico;

        function pararRolagem(btn) {
            if (estado.intervalo) {
                win.clearInterval(estado.intervalo);
                estado.intervalo = null;
            }
            estado.rolando = false;
            if (btn) btn.textContent = 'Rolar';
        }

        function alternarRolagem(btn) {
            if (estado.rolando) {
                pararRolagem(btn);
                return;
            }
            estado.rolando = true;
            btn.textContent = 'Parar';
            estado.intervalo = win.setInterval(function() {
                win.scrollBy(0, 1);
                var alturaTotal = win.document.documentElement.scrollHeight;
                if (win.scrollY + win.innerHeight >= alturaTotal - 2) {
                    pararRolagem(btn);
                }
            }, 40);
        }

        function garantirBotao() {
            var btn = doc.getElementById('btn-rolar-automatico');
            if (!btn) {
                btn = doc.createElement('button');
                btn.id = 'btn-rolar-automatico';
                btn.type = 'button';
                btn.style.position = 'fixed';
                btn.style.bottom = '90px';
                btn.style.right = '20px';
                btn.style.zIndex = '999999';
                btn.style.padding = '0.5rem 1rem';
                btn.style.borderRadius = '999px';
                btn.style.border = '1px solid COR_MUTADO';
                btn.style.backgroundColor = 'COR_FUNDO';
                btn.style.color = 'COR_TEXTO';
                btn.style.cursor = 'pointer';
                btn.style.fontSize = '0.85rem';
                btn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.25)';
                doc.body.appendChild(btn);
            }
            btn.textContent = estado.rolando ? 'Parar' : 'Rolar';
            btn.onclick = function() { alternarRolagem(btn); };
            btn.style.display = mostrar ? 'block' : 'none';
            if (!mostrar) {
                pararRolagem(btn);
            }
        }

        garantirBotao();
    })();
    </script>
    """
    .replace("MOSTRAR_FLAG", "true" if pagina == "Plano de Leitura" else "false")
    .replace("COR_MUTADO", cor_mutado)
    .replace("COR_FUNDO", cor_fundo)
    .replace("COR_TEXTO", cor_texto),
    height=0,
)

st.markdown('<div class="bloco-central">', unsafe_allow_html=True)
st.markdown("# Explore a Biblia")
st.markdown(
    "*Pergunte e descubra passagens biblicas com compreensao semantica "
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

    idx_hoje, total, _ = capitulo_do_dia(0)

    if st.session_state.auto_hoje:
        st.session_state.offset_leitura = 0

    idx, total, capitulo = capitulo_do_dia(st.session_state.offset_leitura)
    semana_atual, dia_atual = semana_dia_de_indice(idx)

    with st.sidebar:
        with st.container(border=True, key="sb_plano"):
            st.caption("PLANO DE LEITURA")
            st.selectbox("Plano", ["Sequencial - 1 capitulo/dia"], disabled=True)
            st.markdown("**Biblia Ave Maria - ordem canonica**")
            st.caption(
                "Um capitulo por dia, do Genesis ao Apocalipse, seguindo a "
                "ordem dos livros da Biblia Catolica Ave Maria (nao e um "
                "plano cronologico)."
            )

        with st.container(border=True, key="sb_semana_dia"):
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

        with st.container(border=True, key="sb_leitura_atual"):
            st.text_input(
                "Leitura atual",
                value=f"{capitulo['livro']} {capitulo['capitulo']}",
                disabled=True,
                label_visibility="collapsed",
            )

            with st.container(key="sb_audio"):
                texto_audio_js = json.dumps(texto_para_audio(capitulo))
                components.html(
                    """
                    <style>
                    html, body { margin: 0; padding: 0; overflow: hidden; }
                    #btn-audio-capitulo {
                        width: 100%;
                        min-height: 1.6rem;
                        padding: 0.1rem 0.5rem;
                        font-size: 0.76rem;
                        font-family: "Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                        background-color: COR_FUNDO;
                        color: COR_TEXTO;
                        border: 1px solid COR_MUTADO;
                        border-radius: 0.5rem;
                        cursor: pointer;
                    }
                    #btn-audio-capitulo:hover {
                        border-color: COR_DESTAQUE;
                        color: COR_DESTAQUE;
                    }
                    </style>
                    <button id="btn-audio-capitulo" type="button">Ouvir capitulo</button>
                    <script>
                    (function() {
                        var btn = document.getElementById('btn-audio-capitulo');
                        var texto = TEXTO_JSON;
                        var ROTULO_OUVIR = 'Ouvir capitulo';
                        var ROTULO_PARAR = 'Parar audio';
                        btn.textContent = ROTULO_OUVIR;

                        btn.addEventListener('click', function() {
                            if (window.speechSynthesis.speaking) {
                                window.speechSynthesis.cancel();
                                btn.textContent = ROTULO_OUVIR;
                                return;
                            }
                            var utterance = new SpeechSynthesisUtterance(texto);
                            utterance.lang = 'pt-BR';
                            utterance.rate = 0.95;
                            utterance.onend = function() { btn.textContent = ROTULO_OUVIR; };
                            utterance.onerror = function() { btn.textContent = ROTULO_OUVIR; };
                            window.speechSynthesis.speak(utterance);
                            btn.textContent = ROTULO_PARAR;
                        });
                    })();
                    </script>
                    """
                    .replace("TEXTO_JSON", texto_audio_js)
                    .replace("COR_FUNDO", cor_fundo)
                    .replace("COR_TEXTO", cor_texto)
                    .replace("COR_MUTADO", cor_mutado)
                    .replace("COR_DESTAQUE", cor_destaque),
                    height=40,
                )
        with st.container(border=True, key="sb_progresso"):
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

with st.container(key="rodape_pagina"):
    st.markdown(
        f"""
        <hr style="margin-top: 3rem; border-color: {cor_mutado}; width: 100vw; max-width: 100vw; margin-left: calc(-50vw + 50%); margin-right: calc(-50vw + 50%);">
        <p style="text-align: center; color: {cor_mutado}; font-size: 0.85rem;">
            Feito por armandonettox &middot; texto: Biblia Catolica Ave Maria
        </p>
        """,
        unsafe_allow_html=True,
    )
