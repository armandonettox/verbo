import re
from datetime import date

import streamlit as st
import streamlit.components.v1 as components
from modules.busca import buscar_versiculos
from modules.resposta import gerar_resposta
from modules.leitura import carregar_capitulos, texto_para_audio
from modules.plano_livre import listar_livros, _renderizar_lista_livros, _renderizar_grade_capitulos
from modules.plano_versiculo_dia import obter_versiculo_do_dia
from modules.audio_widget import renderizar_audio
from modules.fuso_horario import garantir_data_local

TAMANHO_RESUMO_VERSICULO = 220
QUANTIDADE_VERSICULOS_POR_PAGINA = 4


def _resumir_texto(texto, tamanho=TAMANHO_RESUMO_VERSICULO):
    if len(texto) <= tamanho:
        return texto
    return texto[:tamanho].rsplit(" ", 1)[0] + "..."


def _localizar_capitulo(capitulos, referencia):
    m = re.match(r"^(.+) (\d+):\d+(?:-\d+)?$", referencia)
    if not m:
        return None
    livro, num_capitulo = m.group(1), int(m.group(2))
    for idx, capitulo in enumerate(capitulos):
        if capitulo["livro"] == livro and capitulo["capitulo"] == num_capitulo:
            return idx
    return None


@st.fragment
def _renderizar_busca_semantica(capitulos_leitura):
    st.markdown(
        '<div class="bloco-central">'
        "<h1>Explore a Biblia</h1>"
        "<p><em>Pergunte e descubra passagens biblicas com compreensao "
        "semantica e insights contextuais.</em></p>"
        "</div>",
        unsafe_allow_html=True,
    )

    if "busca_pendente" not in st.session_state:
        st.session_state.busca_pendente = False

    def _marcar_busca_pendente():
        st.session_state.busca_pendente = True

    with st.form("busca_form"):
        col_campo, col_botao = st.columns([5, 1])
        with col_campo:
            pergunta = st.text_input(
                "Qual e a sua pergunta?",
                label_visibility="collapsed",
                placeholder="O que Jesus disse sobre o amor ao proximo?",
                key="busca_pergunta",
            )
        with col_botao:
            esta_buscando = st.session_state.busca_pendente
            st.form_submit_button(
                "Buscando" if esta_buscando else "Buscar",
                icon=":material/progress_activity:" if esta_buscando else ":material/search:",
                use_container_width=True,
                disabled=esta_buscando,
                key="busca_botao",
                on_click=_marcar_busca_pendente,
            )

    if st.session_state.busca_pendente and pergunta:
        with st.spinner("Buscando versiculos..."):
            versiculos = buscar_versiculos(pergunta)

        resposta = gerar_resposta(pergunta, versiculos)

        st.session_state.busca_pendente = False
        st.session_state.ultima_busca = {"resposta": resposta, "versiculos": versiculos}
        st.session_state.versiculos_visiveis = QUANTIDADE_VERSICULOS_POR_PAGINA
        st.rerun()
    elif st.session_state.busca_pendente:
        st.session_state.busca_pendente = False

    ultima_busca = st.session_state.get("ultima_busca")
    if ultima_busca:
        total_versiculos = len(ultima_busca["versiculos"])
        tags = "".join(
            f'<span class="tag-versiculo">{v["referencia"]}</span>'
            for v in ultima_busca["versiculos"]
        )
        with st.container(border=False, key="insights_busca"):
            st.markdown(
                f'<p class="insights-texto">Busca concluida &middot; '
                f"{total_versiculos} versiculos semelhantes encontrados</p>"
                '<div class="tags-scroll-wrapper">'
                '<button type="button" class="tag-seta" id="tag_seta_esquerda" '
                'aria-label="Ver tags anteriores">&#8249;</button>'
                f'<div class="tags-versiculos" id="tags_versiculos_scroll">{tags}</div>'
                '<button type="button" class="tag-seta" id="tag_seta_direita" '
                'aria-label="Ver mais tags">&#8250;</button>'
                "</div>",
                unsafe_allow_html=True,
            )

        components.html(
            """
            <script>
            (function() {
                var doc = window.parent.document;
                function configurar() {
                    var scroller = doc.getElementById('tags_versiculos_scroll');
                    var esquerda = doc.getElementById('tag_seta_esquerda');
                    var direita = doc.getElementById('tag_seta_direita');
                    if (!scroller || !esquerda || !direita) return;
                    if (scroller.dataset.setasConfiguradas) return;
                    scroller.dataset.setasConfiguradas = '1';
                    esquerda.addEventListener('click', function() {
                        scroller.scrollBy({left: -160, behavior: 'smooth'});
                    });
                    direita.addEventListener('click', function() {
                        scroller.scrollBy({left: 160, behavior: 'smooth'});
                    });
                }
                configurar();
                var obs = new MutationObserver(function() {
                    try { configurar(); } catch (e) {}
                });
                obs.observe(doc.body, {childList: true, subtree: true});
            })();
            </script>
            """,
            height=0,
        )

        with st.container(border=True, key="resposta_card"):
            st.write(ultima_busca["resposta"])

        if "versiculos_visiveis" not in st.session_state:
            st.session_state.versiculos_visiveis = QUANTIDADE_VERSICULOS_POR_PAGINA

        versiculos_visiveis = ultima_busca["versiculos"][: st.session_state.versiculos_visiveis]
        for i, v in enumerate(versiculos_visiveis):
            with st.container(border=True, key=f"versiculo_card_{i}"):
                st.markdown(
                    f"**{v['referencia']}**"
                    f"<style>.st-key-versiculo_btn_ver_{i} button::before "
                    f'{{ content: "{v.get("similaridade", 0):.2f}% similar"; }}</style>',
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Ver versiculo",
                    icon=":material/open_in_new:",
                    key=f"versiculo_btn_ver_{i}",
                ):
                    idx_capitulo = _localizar_capitulo(capitulos_leitura, v["referencia"])
                    if idx_capitulo is not None:
                        st.session_state.capitulo_aberto = idx_capitulo
                        st.rerun()
                st.write(_resumir_texto(v["texto"]))

        if st.session_state.versiculos_visiveis < total_versiculos:
            if st.button("Mostrar mais resultados", use_container_width=True, key="btn_mostrar_mais"):
                st.session_state.versiculos_visiveis += QUANTIDADE_VERSICULOS_POR_PAGINA
                st.rerun(scope="fragment")

    else:
        data_hoje = st.session_state.get("data_local_usuario", date.today())
        versiculo_dia = obter_versiculo_do_dia(data_hoje)
        with st.container(border=True, key="card_leitura_dia"):
            st.caption("LEITURA DO DIA")
            st.markdown(f"**{versiculo_dia['referencia']}**")
            st.write(versiculo_dia["texto"])

st.set_page_config(page_title="Verbo", page_icon="assets/favicon.png", layout="wide")

garantir_data_local()

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
    [data-testid="InputInstructions"] {{ display: none !important; }}
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
    .st-key-conteudo_pagina {{
        max-width: 900px;
        margin: 0 auto;
        width: 100%;
    }}

    [data-testid="stAppViewContainer"] {{ background-color: {cor_fundo}; }}
    [data-testid="stSidebar"] {{ background-color: {cor_fundo}; }}
    [data-testid="stSidebar"][aria-expanded="true"] {{
        width: 380px !important;
        min-width: 380px !important;
        max-width: 380px !important;
        border-right: 1px solid {cor_mutado};
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
    .st-key-sb_plano, .st-key-sb_semana_dia, .st-key-sb_leitura_atual, .st-key-sb_progresso,
    .st-key-sb_versiculo_data {{
        padding: 0.4rem !important;
        gap: 0.2rem !important;
    }}
    [data-testid="stSidebar"] .stDateInput input {{
        min-height: 1.6rem !important;
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
        font-size: 0.76rem !important;
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
    [data-testid="stSidebar"] [data-baseweb="input"],
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [role="group"],
    [data-testid="stSidebar"] .stButton button {{
        border-color: {cor_destaque} !important;
        transition: box-shadow 0.15s ease;
    }}
    [data-testid="stSidebar"] [data-baseweb="input"]:hover,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [role="group"]:hover,
    [data-testid="stSidebar"] .stButton button:hover {{
        box-shadow: 0 0 0 1px {cor_destaque};
    }}
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

    .st-key-busca_botao button {{
        white-space: nowrap !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
    }}
    .st-key-busca_botao button p {{
        white-space: nowrap !important;
        font-size: 0.85rem !important;
    }}
    .st-key-busca_botao button:disabled span[role="img"],
    .st-key-busca_botao button:disabled [data-testid="stIconMaterial"],
    .st-key-busca_botao button:disabled svg {{
        display: inline-block !important;
        animation: girar 0.9s linear infinite !important;
    }}
    @keyframes girar {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    .insights-texto {{
        text-align: center;
        font-style: italic;
        color: {cor_mutado};
        margin-bottom: 0.6rem;
    }}
    .tags-scroll-wrapper {{
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}
    .tags-versiculos {{
        display: flex;
        flex-wrap: nowrap;
        overflow-x: auto;
        gap: 0.4rem;
        scroll-behavior: smooth;
        scrollbar-width: none;
    }}
    .tags-versiculos::-webkit-scrollbar {{ display: none; }}
    .tag-versiculo {{
        background-color: {cor_fundo_2};
        border: 1px solid {cor_mutado};
        border-radius: 999px;
        padding: 0.2rem 0.7rem;
        font-size: 0.8rem;
        white-space: nowrap;
        flex-shrink: 0;
    }}
    .tag-seta {{
        background: none;
        border: 1px solid {cor_mutado};
        border-radius: 50%;
        width: 1.8rem;
        height: 1.8rem;
        min-width: 1.8rem;
        color: {cor_mutado};
        cursor: pointer;
        font-size: 1.1rem;
        line-height: 1;
        flex-shrink: 0;
    }}
    .tag-seta:hover {{
        color: {cor_destaque};
        border-color: {cor_destaque};
    }}

    [class*="st-key-versiculo_card_"] {{
        position: relative !important;
    }}
    [class*="st-key-versiculo_btn_ver_"] {{
        position: absolute !important;
        top: 0.7rem !important;
        right: 0.7rem !important;
        left: auto !important;
        width: auto !important;
        margin: 0 !important;
        z-index: 2;
    }}
    [class*="st-key-versiculo_btn_ver_"] button {{
        white-space: nowrap !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        min-height: 1.8rem !important;
    }}
    [class*="st-key-versiculo_btn_ver_"] button p {{
        white-space: nowrap !important;
        font-size: 0.72rem !important;
    }}
    [class*="st-key-versiculo_btn_ver_"] button {{
        position: relative !important;
    }}
    [class*="st-key-versiculo_btn_ver_"] button::before {{
        position: absolute;
        top: 50%;
        right: 100%;
        transform: translateY(-50%);
        margin-right: 0.5rem;
        background-color: {cor_fundo_2};
        border: 1px solid {cor_mutado};
        border-radius: 999px;
        padding: 0.15rem 0.6rem;
        font-size: 0.7rem;
        white-space: nowrap;
        color: {cor_mutado};
    }}

    .bloco-central {{ text-align: center; margin-bottom: 1.5rem; }}
    .bloco-central h1 {{ font-size: 2.75rem; margin-bottom: 0.5rem; }}
    .bloco-central p {{ color: {cor_mutado} !important; font-style: italic; font-size: 1.05rem; }}
    .bloco-central [data-testid="stHeaderActionElements"] {{ display: none; }}

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

    .st-key-tz_detector {{
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        overflow: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }}

    div[data-testid="stElementContainer"]:has(> iframe) {{
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
        line-height: 0 !important;
    }}
    [class*="st-key-sb_audio"] div[data-testid="stElementContainer"]:has(> iframe),
    [class*="st-key-audio_"] div[data-testid="stElementContainer"]:has(> iframe) {{
        height: 40px !important;
        min-height: 40px !important;
        line-height: normal !important;
    }}
    [class*="st-key-sb_audio"] iframe,
    [class*="st-key-audio_"] iframe {{ height: 40px !important; }}
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
    col_vazio, col_logo, col_espaco, col_acoes = st.columns([1.8, 2, 0.2, 1.6])
    with col_logo:
        with st.container(key="logo_center"):
            st.image("assets/logo.png", width=44)
    with col_acoes:
        col_sidebar, col_git, col_tema = st.columns([1, 1, 1], gap="small")
        with col_sidebar:
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

if "capitulo_aberto" not in st.session_state:
    st.session_state.capitulo_aberto = None

capitulos_leitura = carregar_capitulos()
idx_aberto = st.session_state.capitulo_aberto

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

        function obterContainerRolagem() {
            return doc.querySelector('[data-testid="stMain"]') || doc.scrollingElement || doc.documentElement;
        }

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
            var container = obterContainerRolagem();
            estado.intervalo = win.setInterval(function() {
                container.scrollBy(0, 1);
                if (container.scrollTop + container.clientHeight >= container.scrollHeight - 2) {
                    pararRolagem(btn);
                }
            }, 40);
        }

        function temConteudoRolavel(container) {
            return container.scrollHeight > container.clientHeight + 4;
        }

        function garantirBotao() {
            var antigos = doc.querySelectorAll('#btn-rolar-automatico');
            for (var i = 0; i < antigos.length; i++) {
                antigos[i].parentNode.removeChild(antigos[i]);
            }

            var btn = doc.createElement('button');
            btn.id = 'btn-rolar-automatico';
            btn.type = 'button';
            btn.style.position = 'fixed';
            btn.style.bottom = '90px';
            btn.style.right = '20px';
            btn.style.zIndex = '2147483647';
            btn.style.padding = '0.5rem 1rem';
            btn.style.borderRadius = '999px';
            btn.style.border = '1px solid COR_MUTADO';
            btn.style.backgroundColor = 'COR_FUNDO';
            btn.style.color = 'COR_TEXTO';
            btn.style.cursor = 'pointer';
            btn.style.fontSize = '0.85rem';
            btn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.25)';
            btn.style.pointerEvents = 'auto';
            btn.textContent = estado.rolando ? 'Parar' : 'Rolar';
            btn.onclick = function() { alternarRolagem(btn); };
            doc.body.appendChild(btn);

            var container = obterContainerRolagem();

            function atualizarVisibilidade() {
                var visivel = mostrar && temConteudoRolavel(container);
                btn.style.display = visivel ? 'block' : 'none';
                if (!visivel) {
                    pararRolagem(btn);
                }
            }

            atualizarVisibilidade();
            win.addEventListener('resize', atualizarVisibilidade);

            var observador = new MutationObserver(atualizarVisibilidade);
            observador.observe(container, {childList: true, subtree: true, characterData: true});
        }

        garantirBotao();
    })();
    </script>
    """
    .replace("MOSTRAR_FLAG", "true" if idx_aberto is not None else "false")
    .replace("COR_MUTADO", cor_mutado)
    .replace("COR_FUNDO", cor_fundo)
    .replace("COR_TEXTO", cor_texto),
    height=0,
)

if "livro_selecionado" not in st.session_state:
    st.session_state.livro_selecionado = None

ultima_busca = st.session_state.get("ultima_busca")


def _iniciar_nova_busca():
    st.session_state.ultima_busca = None
    st.session_state.historico_chat = []
    st.session_state.versiculos_visiveis = QUANTIDADE_VERSICULOS_POR_PAGINA
    st.session_state.capitulo_aberto = None
    st.session_state.livro_selecionado = None


with st.sidebar:
    if ultima_busca:
        with st.container(border=True, key="sb_fontes"):
            st.caption("VERSICULOS ENCONTRADOS")
            if st.button("Nova busca", icon=":material/refresh:", use_container_width=True, key="btn_nova_busca"):
                _iniciar_nova_busca()
                st.rerun()
            for i, v in enumerate(ultima_busca["versiculos"]):
                if st.button(v["referencia"], key=f"fonte_{i}", use_container_width=True):
                    idx_capitulo = _localizar_capitulo(capitulos_leitura, v["referencia"])
                    if idx_capitulo is not None:
                        st.session_state.capitulo_aberto = idx_capitulo
                        st.rerun()
    else:
        with st.container(border=True, key="sb_livros"):
            st.caption("ESCOLHA O LIVRO")
            _renderizar_lista_livros(listar_livros(capitulos_leitura), prefixo_key="painel_livro")

with st.container(key="conteudo_pagina"):
    col_centro, col_direita = st.columns([2.2, 1])

    with col_centro:
        if idx_aberto is not None:
            capitulo = capitulos_leitura[idx_aberto]

            if st.button("Voltar para busca", icon=":material/arrow_back:", key="capitulo_btn_voltar"):
                st.session_state.capitulo_aberto = None
                st.rerun()

            st.markdown(f"### {capitulo['livro']} {capitulo['capitulo']}")
            st.write(capitulo["texto"])

            renderizar_audio(
                texto_para_audio(capitulo),
                key="audio_capitulo",
                cor_fundo=cor_fundo,
                cor_texto=cor_texto,
                cor_mutado=cor_mutado,
                cor_destaque=cor_destaque,
                rotulo="Ouvir capitulo",
            )

            col_anterior, col_proximo = st.columns(2)
            with col_anterior:
                if st.button(
                    "Capitulo Anterior",
                    use_container_width=True,
                    key="capitulo_btn_anterior",
                    disabled=idx_aberto == 0,
                ):
                    st.session_state.capitulo_aberto = idx_aberto - 1
                    st.rerun()
            with col_proximo:
                if st.button(
                    "Proximo Capitulo",
                    use_container_width=True,
                    key="capitulo_btn_proximo",
                    disabled=idx_aberto == len(capitulos_leitura) - 1,
                ):
                    st.session_state.capitulo_aberto = idx_aberto + 1
                    st.rerun()

        else:
            _renderizar_busca_semantica(capitulos_leitura)

    with col_direita:
        with st.container(border=True, key="painel_direito"):
            livro_selecionado = st.session_state.livro_selecionado
            if ultima_busca:
                st.caption("CONTINUE A CONVERSA")
                st.markdown(
                    "Depois da resposta, faca perguntas de acompanhamento "
                    "sobre os mesmos versiculos encontrados."
                )
            elif livro_selecionado:
                if st.button("Voltar aos livros", icon=":material/arrow_back:", key="btn_voltar_livros"):
                    st.session_state.livro_selecionado = None
                    st.rerun()
                st.markdown(f"**{livro_selecionado['livro']}**")
                _renderizar_grade_capitulos(livro_selecionado, capitulos_leitura, prefixo_key="painel_capitulo")
            else:
                st.caption("COMO NAVEGAR")
                st.markdown(
                    "Escolha um livro na lateral ou digite uma pergunta na busca "
                    "para explorar a Biblia."
                )

with st.container(key="rodape_pagina"):
    st.markdown(
        f"""
        <hr style="margin-top: 3rem; border-color: {cor_mutado}; width: 100vw; max-width: 100vw; margin-left: calc(-50vw + 50%); margin-right: calc(-50vw + 50%);">
        <style>
        [data-testid="stMarkdownContainer"] a.rodape-link {{ color: {cor_destaque} !important; text-decoration: none !important; }}
        [data-testid="stMarkdownContainer"] a.rodape-link:hover {{ text-decoration: underline !important; }}
        </style>
        <p style="text-align: center; color: {cor_mutado}; font-size: 0.85rem; margin-bottom: 0.25rem;">
            Feito por <a class="rodape-link" href="https://armandonetto.com/" target="_blank">Armando Netto</a>
            &middot; Fonte: <a class="rodape-link" href="https://github.com/fidalgobr/bibliaAveMariaJSON" target="_blank">Biblia Catolica Ave Maria</a>
        </p>
        <p style="text-align: center; color: {cor_mutado}; font-size: 0.75rem;">
            Codigo sob licenca <a class="rodape-link" href="https://github.com/armandonettox/verbo/blob/main/LICENSE" target="_blank">PolyForm Noncommercial 1.0.0</a>
        </p>
        """,
        unsafe_allow_html=True,
    )
