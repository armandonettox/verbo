import re
from datetime import date

import streamlit as st
import streamlit.components.v1 as components
from modules.busca import buscar_versiculos
from modules.resposta import gerar_resposta, continuar_conversa
from modules.leitura import carregar_capitulos, texto_para_audio
from modules.plano_livre import _renderizar_seletor_livro_capitulo
from modules.plano_versiculo_dia import obter_versiculo_do_dia
from modules.audio_widget import renderizar_audio, renderizar_audio_com_progresso
from modules.acoes_chat import renderizar_botao_copiar, renderizar_botao_compartilhar
from modules.fuso_horario import garantir_data_local, agora_local
from modules.erros import mensagem_erro_ia

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
    hoje = st.session_state.get("data_local_usuario", date.today())
    if quando.date() == hoje:
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
            try:
                with st.spinner(""):
                    versiculos = buscar_versiculos(pergunta)
                resposta = gerar_resposta(pergunta, versiculos)
            except Exception as excecao:
                st.session_state.busca_pendente = False
                st.toast(mensagem_erro_ia(excecao), icon=":material/error:")
                st.rerun()
            else:
                st.session_state.busca_pendente = False
                st.session_state.ultima_busca = {
                    "pergunta": pergunta,
                    "resposta": resposta,
                    "versiculos": versiculos,
                    "quando": agora_local(),
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
        quando_original = ultima_busca.get("quando", agora_local())

        def _regenerar_original():
            try:
                nova_resposta = gerar_resposta(ultima_busca["pergunta"], ultima_busca["versiculos"])
            except Exception as excecao:
                st.session_state.regenerando_alvo = None
                st.toast(mensagem_erro_ia(excecao), icon=":material/error:")
                st.rerun(scope="fragment")
            else:
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
                try:
                    nova_resposta = continuar_conversa(
                        ultima_busca["pergunta"],
                        ultima_busca["resposta"],
                        ultima_busca["versiculos"],
                        historico_para_llm,
                        pergunta_usuario,
                    )
                except Exception as excecao:
                    st.session_state.regenerando_alvo = None
                    st.toast(mensagem_erro_ia(excecao), icon=":material/error:")
                    st.rerun(scope="fragment")
                else:
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
            agora = agora_local()
            st.session_state.historico_chat.append({"role": "user", "content": pergunta_seguimento, "quando": agora})
            st.session_state.historico_chat.append({"role": "assistant", "content": "", "quando": agora})
            st.session_state.regenerando_alvo = len(st.session_state.historico_chat) - 1
            st.rerun(scope="fragment")

st.set_page_config(page_title="Verbo", page_icon="assets/favicon.png", layout="wide")

with open("assets/templates/definir-idioma.html", encoding="utf-8") as f:
    components.html(f.read(), height=0)

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

with open("assets/estilo.css", encoding="utf-8") as f:
    _css_estatico = f.read()

st.markdown(
    f"""
    <style>
    :root {{
        --cor-fundo: {cor_fundo};
        --cor-fundo-2: {cor_fundo_2};
        --cor-texto: {cor_texto};
        --cor-mutado: {cor_mutado};
        --cor-destaque: {cor_destaque};
    }}
    {_css_estatico}
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

with open("assets/templates/rolagem-automatica.html", encoding="utf-8") as f:
    _script_rolagem = f.read()

components.html(
    _script_rolagem
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
