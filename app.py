import re
from datetime import date, datetime

import streamlit as st
import streamlit.components.v1 as components
from modules.busca import buscar_versiculos
from modules.resposta import gerar_resposta, continuar_conversa
from modules.leitura import carregar_capitulos, texto_para_audio
from modules.plano_livre import _renderizar_seletor_livro_capitulo
from modules.plano_versiculo_dia import obter_versiculo_do_dia
from modules.audio_widget import renderizar_audio, renderizar_audio_com_progresso
from modules.acoes_chat import renderizar_botao_copiar, renderizar_botao_compartilhar
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


def _formatar_quando(quando):
    if quando.date() == date.today():
        return f"Hoje {quando.strftime('%H:%M')}"
    return quando.strftime("%d/%m/%Y %H:%M")


def _marcar_regenerando(alvo):
    st.session_state.regenerando_alvo = alvo


def _renderizar_mensagem_chat(role, conteudo, quando, indice, on_regenerar=None):
    prefixo = "chat_msg_usuario" if role == "user" else "chat_msg_assistente"
    esta_regenerando = role == "assistant" and st.session_state.get("regenerando_alvo") == indice
    with st.container(key=f"{prefixo}_{indice}"):
        if role == "user":
            st.caption(_formatar_quando(quando))
        conteudo_placeholder = st.empty()
        if esta_regenerando:
            with conteudo_placeholder.container():
                with st.spinner(""):
                    on_regenerar()
            return
        with conteudo_placeholder.container():
            st.write(conteudo)
        if role == "assistant":
            with st.container(key=f"acoes_chat_{indice}"):
                col_audio, col_copiar, col_compartilhar, col_regenerar = st.columns(4)
                with col_audio:
                    renderizar_audio(
                        conteudo,
                        key=f"audio_chat_{indice}",
                        cor_fundo=cor_fundo,
                        cor_texto=cor_texto,
                        cor_mutado=cor_mutado,
                        cor_destaque=cor_destaque,
                        icone_apenas=True,
                        tamanho_botao_rem=2.0,
                    )
                with col_copiar:
                    renderizar_botao_copiar(
                        conteudo,
                        key=f"copiar_chat_{indice}",
                        cor_mutado=cor_mutado,
                        cor_destaque=cor_destaque,
                    )
                with col_compartilhar:
                    renderizar_botao_compartilhar(
                        conteudo,
                        key=f"compartilhar_chat_{indice}",
                        cor_mutado=cor_mutado,
                        cor_destaque=cor_destaque,
                    )
                with col_regenerar:
                    if on_regenerar is not None:
                        st.button(
                            "",
                            icon=":material/refresh:",
                            key=f"regenerar_chat_{indice}",
                            help="Gerar novamente",
                            on_click=_marcar_regenerando,
                            args=(indice,),
                        )


@st.fragment
def _renderizar_busca_semantica(capitulos_leitura):
    ultima_busca = st.session_state.get("ultima_busca")

    if "busca_pendente" not in st.session_state:
        st.session_state.busca_pendente = False
    if "regenerando_alvo" not in st.session_state:
        st.session_state.regenerando_alvo = None

    if st.session_state.regenerando_alvo is not None:
        st.markdown(
            f"<style>.st-key-chat_msg_assistente_{st.session_state.regenerando_alvo} "
            "[data-stale='true'] { display: none !important; }</style>",
            unsafe_allow_html=True,
        )

    def _marcar_busca_pendente():
        if st.session_state.get("busca_pergunta", "").strip():
            st.session_state.busca_pendente = True

    if not ultima_busca:
        with st.container(key="logo_central"):
            st.image("assets/logo.png", width=90)

        st.markdown(
            '<div class="bloco-central">'
            "<h1>Explore a Biblia</h1>"
            "<p><em>Pergunte e descubra passagens biblicas com compreensao "
            "semantica e insights contextuais.</em></p>"
            "</div>",
            unsafe_allow_html=True,
        )

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
            with st.spinner(""):
                versiculos = buscar_versiculos(pergunta)

            resposta = gerar_resposta(pergunta, versiculos)

            st.session_state.busca_pendente = False
            st.session_state.ultima_busca = {
                "pergunta": pergunta,
                "resposta": resposta,
                "versiculos": versiculos,
                "quando": datetime.now(),
            }
            st.session_state.versiculos_visiveis = QUANTIDADE_VERSICULOS_POR_PAGINA
            st.session_state.historico_chat = []
            st.rerun()
        elif st.session_state.busca_pendente:
            st.session_state.busca_pendente = False

        data_hoje = st.session_state.get("data_local_usuario", date.today())
        versiculo_dia = obter_versiculo_do_dia(data_hoje)
        with st.container(border=True, key="card_leitura_dia"):
            st.caption("LEITURA DO DIA")
            renderizar_audio(
                versiculo_dia["texto"],
                key="audio_versiculo_dia",
                cor_fundo=cor_fundo,
                cor_texto=cor_texto,
                cor_mutado=cor_mutado,
                cor_destaque=cor_destaque,
                icone_apenas=True,
            )
            st.markdown(f"**{versiculo_dia['referencia']}**")
            st.write(versiculo_dia["texto"])

    else:
        quando_original = ultima_busca.get("quando", datetime.now())

        def _regenerar_original():
            nova_resposta = gerar_resposta(ultima_busca["pergunta"], ultima_busca["versiculos"])
            st.session_state.ultima_busca["resposta"] = nova_resposta
            st.session_state.regenerando_alvo = None
            st.rerun(scope="fragment")

        def _criar_regenerar_turno(indice):
            def _regenerar():
                historico = st.session_state.historico_chat
                pergunta_usuario = historico[indice - 1]["content"]
                historico_para_llm = [
                    {"role": t["role"], "content": t["content"]} for t in historico[: indice - 1]
                ]
                nova_resposta = continuar_conversa(
                    ultima_busca["pergunta"],
                    ultima_busca["resposta"],
                    ultima_busca["versiculos"],
                    historico_para_llm,
                    pergunta_usuario,
                )
                st.session_state.historico_chat[indice]["content"] = nova_resposta
                st.session_state.regenerando_alvo = None
                st.rerun(scope="fragment")

            return _regenerar

        _renderizar_mensagem_chat("user", ultima_busca["pergunta"], quando_original, "orig_pergunta")
        _renderizar_mensagem_chat(
            "assistant", ultima_busca["resposta"], quando_original, "orig_resposta",
            on_regenerar=_regenerar_original,
        )

        if "historico_chat" not in st.session_state:
            st.session_state.historico_chat = []

        for i, turno in enumerate(st.session_state.historico_chat):
            on_regenerar = _criar_regenerar_turno(i) if turno["role"] == "assistant" else None
            _renderizar_mensagem_chat(turno["role"], turno["content"], turno["quando"], i, on_regenerar=on_regenerar)

        st.markdown('<div class="espaco_chat_fixo"></div>', unsafe_allow_html=True)

        with st.container(key="chat_conversa"):
            pergunta_seguimento = st.chat_input(
                "Faca uma pergunta de acompanhamento...",
                key="chat_input_seguimento",
            )
            with st.container(key="aviso_ia_chat"):
                st.caption("Respostas geradas por IA a partir dos versiculos encontrados. Confira sempre o texto original.")
        if pergunta_seguimento:
            agora = datetime.now()
            st.session_state.historico_chat.append({"role": "user", "content": pergunta_seguimento, "quando": agora})
            st.session_state.historico_chat.append({"role": "assistant", "content": "", "quando": agora})
            st.session_state.regenerando_alvo = len(st.session_state.historico_chat) - 1
            st.rerun(scope="fragment")

st.set_page_config(page_title="Verbo", page_icon="assets/favicon.png", layout="wide")

garantir_data_local()

if "tema_escuro" not in st.session_state:
    st.session_state.tema_escuro = False

if st.session_state.tema_escuro:
    cor_fundo, cor_fundo_2, cor_texto, cor_mutado = (
        "#221A12", "#33281B", "#F1E8D8", "#C9B79E"
    )
else:
    cor_fundo, cor_fundo_2, cor_texto, cor_mutado = (
        "#FBF6EC", "#F1E8D8", "#3B2A1E", "#6B4F3A"
    )
cor_destaque = "#B8860B"

st.markdown(
    f"""
    <style>
    [data-testid="stHeader"] {{
        background: transparent !important;
        box-shadow: none !important;
        height: 2.75rem !important;
        min-height: 2.75rem !important;
    }}
    [data-testid="stToolbarActions"] {{ display: none !important; }}
    [data-testid="stStatusWidget"] {{ display: none !important; }}
    [data-testid="stMainMenu"] {{ display: none !important; }}
    [data-testid="stAppDeployButton"] {{ display: none !important; }}
    [data-testid="InputInstructions"] {{ display: none !important; }}
    [data-testid="stExpandSidebarButton"] {{ z-index: 999999 !important; }}
    [data-testid="stSidebarCollapseButton"] span[data-testid="stIconMaterial"],
    [data-testid="stExpandSidebarButton"] span[data-testid="stIconMaterial"] {{
        color: {cor_mutado} !important;
    }}
    [data-testid="stVerticalBlock"], [data-testid="stForm"] {{
        border-color: {cor_mutado} !important;
    }}
    [data-testid="stBottom"] {{ display: none; }}
    [data-testid="stMain"] {{ padding-top: 0 !important; }}
    .espaco_rodape {{ height: 6rem; }}
    .espaco_chat_fixo {{ height: 6rem; }}
    .st-key-chat_conversa {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        width: auto !important;
        z-index: 999;
        background-color: {cor_fundo};
        padding: 0.75rem 1.5rem 1rem;
        box-sizing: border-box;
    }}
    .st-key-chat_conversa [data-testid="stChatInput"] {{
        max-width: 900px;
        margin: 0 auto;
    }}
    .st-key-aviso_ia_chat [data-testid="stCaptionContainer"] {{
        width: 100% !important;
        text-align: center !important;
    }}
    .st-key-aviso_ia_chat [data-testid="stCaptionContainer"] p {{
        font-size: 0.75rem !important;
        color: {cor_mutado} !important;
        margin: 0.4rem 0 0 0 !important;
    }}
    [data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="true"]) .st-key-chat_conversa {{
        left: 380px;
    }}
    [data-testid="stAppViewContainer"] {{ padding-top: 0 !important; }}
    .block-container {{
        padding-top: 2.5rem !important;
        min-height: 100vh !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
    }}
    .st-key-conteudo_pagina {{
        max-width: 900px;
        margin: 0 auto;
        width: 100%;
    }}

    [data-testid="stAppViewContainer"] {{ background-color: {cor_fundo}; }}
    [data-testid="stSidebar"] {{ background-color: {cor_fundo}; position: relative; z-index: 1000001; }}
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
    .st-key-sb_idle_bloco {{ margin-top: 12rem !important; }}
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
    .st-key-sb_fontes [data-testid="stVerticalBlock"] {{
        gap: 0.5rem !important;
    }}
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
    .stTextInput input, .stNumberInput input,
    [data-baseweb="select"] > div,
    [data-testid="stSelectbox"] [role="group"] {{
        background-color: {cor_fundo_2} !important;
        color: {cor_texto} !important;
        border-color: {cor_mutado} !important;
    }}
    .stTextInput input::placeholder {{
        color: {cor_mutado} !important;
        opacity: 1 !important;
    }}
    .stTextInput [data-baseweb="input"],
    .stTextInput [data-baseweb="input"] *,
    [data-testid="stTextInputRootElement"],
    [data-testid="stTextInputRootElement"] * {{
        border-color: {cor_mutado} !important;
    }}
    .stButton button, .stFormSubmitButton button {{
        background-color: {cor_fundo};
        color: {cor_texto};
        border: 1px solid {cor_mutado};
    }}
    .st-key-botao_tema button:focus,
    .st-key-botao_tema button:focus-visible,
    .st-key-botao_tema button:active,
    [data-testid="stSidebarCollapseButton"] button:focus,
    [data-testid="stSidebarCollapseButton"] button:focus-visible,
    [data-testid="stSidebarCollapseButton"] button:active,
    [data-testid="stExpandSidebarButton"]:focus,
    [data-testid="stExpandSidebarButton"]:focus-visible,
    [data-testid="stExpandSidebarButton"]:active {{
        outline: none !important;
        box-shadow: none !important;
    }}

    .st-key-botao_tema {{
        position: fixed;
        top: 0.75rem;
        right: 1.5rem;
        z-index: 1000000;
        display: flex;
        align-items: center;
    }}
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

    [class*="st-key-versiculo_card_"] .stCaptionContainer p {{
        margin-bottom: 0 !important;
    }}
    [class*="st-key-versiculo_btn_ver_"] button {{
        white-space: nowrap !important;
        min-height: 1.8rem !important;
    }}
    [class*="st-key-versiculo_btn_ver_"] button p {{
        white-space: nowrap !important;
        font-size: 0.72rem !important;
    }}

    .st-key-card_leitura_dia {{ position: relative; }}
    .st-key-audio_versiculo_dia {{
        position: absolute;
        top: 0.25rem;
        right: 0.25rem;
    }}

    div[data-testid="stVerticalBlock"].st-key-titulo_capitulo_bloco {{
        position: relative !important;
        width: fit-content !important;
        align-self: flex-start !important;
    }}
    .st-key-audio_capitulo {{
        position: absolute;
        top: 50%;
        left: 100%;
        transform: translateY(-50%);
        margin-left: 0.4rem;
        width: 7.5rem;
    }}
    .st-key-audio_capitulo iframe {{ width: 100% !important; }}

    .bloco-central {{ text-align: center; margin-bottom: 1.5rem; }}
    .bloco-central h1 {{ font-size: 2.75rem; margin-bottom: 0.5rem; }}
    .bloco-central p {{ color: {cor_mutado} !important; font-style: italic; font-size: 1.05rem; }}
    [data-testid="stHeaderActionElements"] {{ display: none; }}

    [class*="st-key-chat_msg_usuario_"] {{
        display: flex !important;
        flex-direction: column;
        align-items: flex-end;
        align-self: flex-end !important;
        width: fit-content !important;
        max-width: 75%;
        margin-bottom: 1.2rem;
    }}
    [class*="st-key-chat_msg_usuario_"] .stCaptionContainer {{
        text-align: right;
    }}
    [class*="st-key-chat_msg_usuario_"] [data-testid="stElementContainer"]:not(:has(.stCaptionContainer)) [data-testid="stMarkdownContainer"] {{
        background-color: {cor_fundo_2};
        border: 1px solid {cor_mutado};
        border-radius: 1rem;
        padding: 0.6rem 1rem;
        text-align: left;
    }}
    [class*="st-key-chat_msg_assistente_"] {{
        align-self: flex-start !important;
        width: fit-content !important;
        max-width: 75%;
        margin-bottom: 1.2rem;
    }}
    [class*="st-key-acoes_chat_"] {{
        max-width: 10rem;
        margin-top: 0.25rem;
    }}
    [class*="st-key-acoes_chat_"] [data-testid="stHorizontalBlock"] {{
        gap: 0 !important;
    }}
    [class*="st-key-regenerar_chat_"] button {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: {cor_mutado} !important;
        padding: 0 !important;
        min-height: 2rem !important;
    }}
    [class*="st-key-regenerar_chat_"] button:hover {{
        color: {cor_destaque} !important;
        background-color: transparent !important;
    }}

    .st-key-rodape_pagina {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        width: auto !important;
        z-index: 1000000;
        padding: 0.5rem 1.5rem;
        box-sizing: border-box;
        background-color: {cor_fundo};
    }}
    [data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="true"]) .st-key-rodape_pagina {{
        left: 380px;
    }}

    .st-key-logo_central {{ display: flex; justify-content: center; align-items: center; margin-bottom: 0.5rem; }}
    .st-key-logo_central img {{
        background-color: #FBF6EC;
        padding: 0.6rem;
        border-radius: 0.75rem;
    }}
    .st-key-logo_central [data-testid="StyledFullScreenButton"] {{ display: none; }}
    .st-key-logo_central [data-testid="stElementToolbar"] {{ display: none; }}

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
    [class*="st-key-audio_"]:not(.st-key-audio_capitulo) div[data-testid="stElementContainer"]:has(> iframe) {{
        height: 40px !important;
        min-height: 40px !important;
        line-height: normal !important;
    }}
    [class*="st-key-sb_audio"] iframe,
    [class*="st-key-audio_"]:not(.st-key-audio_capitulo) iframe {{ height: 40px !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

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

ultima_busca = st.session_state.get("ultima_busca")


def _iniciar_nova_busca():
    st.session_state.ultima_busca = None
    st.session_state.historico_chat = []
    st.session_state.versiculos_visiveis = QUANTIDADE_VERSICULOS_POR_PAGINA
    st.session_state.capitulo_aberto = None


@st.fragment
def _renderizar_sidebar_resultados(capitulos_leitura, ultima_busca):
    with st.container(border=True, key="sb_fontes"):
        st.caption("VERSICULOS ENCONTRADOS")
        if st.button("Nova busca", icon=":material/refresh:", use_container_width=True, key="btn_nova_busca"):
            _iniciar_nova_busca()
            st.rerun()

        if "versiculos_visiveis" not in st.session_state:
            st.session_state.versiculos_visiveis = QUANTIDADE_VERSICULOS_POR_PAGINA

        total_versiculos = len(ultima_busca["versiculos"])
        versiculos_visiveis = ultima_busca["versiculos"][: st.session_state.versiculos_visiveis]
        for i, v in enumerate(versiculos_visiveis):
            with st.container(border=True, key=f"versiculo_card_{i}"):
                st.markdown(f"**{v['referencia']}**")
                st.caption(f"{v.get('similaridade', 0):.2f}% similar")
                if st.button(
                    "Ver versiculo",
                    icon=":material/open_in_new:",
                    key=f"versiculo_btn_ver_{i}",
                    use_container_width=True,
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


@st.fragment
def _renderizar_sidebar_idle(capitulos_leitura):
    with st.container(key="sb_idle_bloco"):
        st.markdown(
            f"<p style='color: {cor_mutado}; font-size: 1.05rem; text-align: center; margin-bottom: 1.5rem;'>"
            "Escolha um livro e capitulo abaixo para ler o texto completo, "
            "ou use a busca ao lado para encontrar versiculos por tema."
            "</p>",
            unsafe_allow_html=True,
        )
        with st.container(border=True, key="sb_livros"):
            st.caption("ESCOLHA O LIVRO E CAPITULO")
            _renderizar_seletor_livro_capitulo(capitulos_leitura)


with st.sidebar:
    if ultima_busca:
        _renderizar_sidebar_resultados(capitulos_leitura, ultima_busca)
    else:
        _renderizar_sidebar_idle(capitulos_leitura)

with st.container(key="conteudo_pagina"):
    if idx_aberto is not None:
        capitulo = capitulos_leitura[idx_aberto]

        if st.button("Voltar para busca", icon=":material/arrow_back:", key="capitulo_btn_voltar"):
            st.session_state.capitulo_aberto = None
            st.rerun()

        with st.container(key="titulo_capitulo_bloco"):
            st.markdown(f"### {capitulo['livro']} {capitulo['capitulo']}")
            renderizar_audio_com_progresso(
                texto_para_audio(capitulo),
                key="audio_capitulo",
                cor_mutado=cor_mutado,
                cor_destaque=cor_destaque,
                tamanho_icone_rem=2.1,
            )

        st.write(capitulo["texto"])

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

        st.markdown('<div class="espaco_rodape"></div>', unsafe_allow_html=True)

    else:
        _renderizar_busca_semantica(capitulos_leitura)

    if not ultima_busca and idx_aberto is None:
        st.markdown('<div class="espaco_rodape"></div>', unsafe_allow_html=True)

if not ultima_busca and idx_aberto is None:
    with st.container(key="rodape_pagina"):
        st.markdown(
            f"""
            <style>
            [data-testid="stMarkdownContainer"] a.rodape-link {{ color: {cor_destaque} !important; text-decoration: none !important; }}
            [data-testid="stMarkdownContainer"] a.rodape-link:hover {{ text-decoration: underline !important; }}
            </style>
            <p style="text-align: center; color: {cor_mutado}; font-size: 0.85rem; margin-bottom: 0.25rem;">
                Feito por <a class="rodape-link" href="https://armandonetto.com/" target="_blank">Armando Netto</a>
            </p>
            <p style="text-align: center; color: {cor_mutado}; font-size: 0.75rem;">
                Protegido sob <a class="rodape-link" href="https://github.com/armandonettox/verbo/blob/main/LICENSE" target="_blank">Licenca Verbo 1.0</a>
            </p>
            """,
            unsafe_allow_html=True,
        )
