from datetime import date

import streamlit as st

from modules.audio_widget import renderizar_audio
from modules.leitura import (
    EPOCA,
    carregar_capitulos,
    dias_na_semana,
    indice_de_semana_dia,
    semana_dia_de_indice,
    texto_para_audio,
    total_semanas,
)

TOTAL_DIAS = 365


@st.cache_data
def distribuir_capitulos(total_capitulos, total_dias=365):
    base = total_capitulos // total_dias
    resto = total_capitulos % total_dias

    distribuicao = []
    cursor = 0
    for dia in range(total_dias):
        quantidade = base + 1 if dia < resto else base
        distribuicao.append((cursor, cursor + quantidade))
        cursor += quantidade
    return distribuicao


def _descricao_intervalo(capitulos_do_dia):
    primeiro = capitulos_do_dia[0]
    ultimo = capitulos_do_dia[-1]

    if len(capitulos_do_dia) == 1:
        return f"{primeiro['livro']} {primeiro['capitulo']}"

    if primeiro["livro"] == ultimo["livro"]:
        return f"{primeiro['livro']} {primeiro['capitulo']}-{ultimo['capitulo']}"

    return f"{primeiro['livro']} {primeiro['capitulo']} - {ultimo['livro']} {ultimo['capitulo']}"


def renderizar(cor_fundo, cor_texto, cor_mutado, cor_destaque):
    if "ano_offset_leitura" not in st.session_state:
        st.session_state.ano_offset_leitura = 0

    todos_capitulos = carregar_capitulos()
    distribuicao = distribuir_capitulos(len(todos_capitulos), TOTAL_DIAS)

    idx_dia_hoje = (date.today() - EPOCA).days % TOTAL_DIAS
    idx_dia = (idx_dia_hoje + st.session_state.ano_offset_leitura) % TOTAL_DIAS

    inicio, fim = distribuicao[idx_dia]
    capitulos_do_dia = todos_capitulos[inicio:fim]

    semana_atual, dia_atual = semana_dia_de_indice(idx_dia)

    # sincroniza os selects com o offset atual antes de instancia-los --
    # depois de criado, o widget nao aceita mais alteracao via session_state
    st.session_state.ano_semana_sel = semana_atual
    st.session_state.ano_dia_sel = dia_atual

    def _semana_alterada():
        semana_sel = st.session_state.ano_semana_sel
        n_dias = dias_na_semana(semana_sel, TOTAL_DIAS)
        dia_sel = min(st.session_state.ano_dia_sel, n_dias)
        novo_idx = indice_de_semana_dia(semana_sel, dia_sel)
        st.session_state.ano_offset_leitura = novo_idx - idx_dia_hoje

    def _dia_alterado():
        novo_idx = indice_de_semana_dia(st.session_state.ano_semana_sel, st.session_state.ano_dia_sel)
        st.session_state.ano_offset_leitura = novo_idx - idx_dia_hoje

    with st.sidebar:
        with st.container(border=True, key="sb_semana_dia"):
            n_semanas = total_semanas(TOTAL_DIAS)
            col_sem, col_dia = st.columns(2)
            with col_sem:
                semana_sel = st.selectbox(
                    "Semana", list(range(1, n_semanas + 1)),
                    key="ano_semana_sel",
                    on_change=_semana_alterada,
                )
            with col_dia:
                n_dias = dias_na_semana(semana_sel, TOTAL_DIAS)
                st.selectbox(
                    "Dia", list(range(1, n_dias + 1)),
                    key="ano_dia_sel",
                    on_change=_dia_alterado,
                )

            if st.session_state.ano_offset_leitura != 0:
                if st.button("Ir para Hoje", use_container_width=True, key="ano_btn_hoje"):
                    st.session_state.ano_offset_leitura = 0
                    st.rerun()

        with st.container(border=True, key="sb_leitura_atual"):
            st.text_input(
                "Leitura atual",
                value=_descricao_intervalo(capitulos_do_dia),
                disabled=True,
                label_visibility="collapsed",
            )

            texto_concatenado = "\n\n".join(
                texto_para_audio(c) for c in capitulos_do_dia
            )
            renderizar_audio(
                texto_concatenado,
                key="sb_audio_ano",
                cor_fundo=cor_fundo,
                cor_texto=cor_texto,
                cor_mutado=cor_mutado,
                cor_destaque=cor_destaque,
                rotulo="Ouvir capitulos",
            )

        with st.container(border=True, key="sb_progresso"):
            st.markdown("**Progresso**")
            st.progress((idx_dia + 1) / TOTAL_DIAS)
            st.caption(f"{idx_dia + 1} / {TOTAL_DIAS} dias ({TOTAL_DIAS - idx_dia - 1} faltam)")

    st.caption(f"Dia {idx_dia + 1} de {TOTAL_DIAS}")
    for capitulo in capitulos_do_dia:
        st.markdown(f"### {capitulo['livro']} {capitulo['capitulo']}")
        st.markdown(capitulo["texto"])

    col_anterior, col_proximo = st.columns(2)
    with col_anterior:
        if st.button("Anterior", use_container_width=True, key="ano_btn_anterior"):
            st.session_state.ano_offset_leitura -= 1
            st.rerun()
    with col_proximo:
        if st.button("Proximo", use_container_width=True, key="ano_btn_proximo"):
            st.session_state.ano_offset_leitura += 1
            st.rerun()
