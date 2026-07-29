import json

import streamlit as st
import streamlit.components.v1 as components


def _icone_copiar(tamanho_px):
    return (
        f'<svg viewBox="0 0 24 24" width="{tamanho_px}" height="{tamanho_px}" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="9" y="9" width="12" height="12" rx="2"/>'
        '<path d="M5 15V5a2 2 0 0 1 2-2h10"/>'
        "</svg>"
    )


def _icone_confirmado(tamanho_px):
    return (
        f'<svg viewBox="0 0 24 24" width="{tamanho_px}" height="{tamanho_px}" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M5 12l5 5L20 7"/>'
        "</svg>"
    )


def _icone_compartilhar(tamanho_px):
    return (
        f'<svg viewBox="0 0 24 24" width="{tamanho_px}" height="{tamanho_px}" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="18" cy="5" r="3"/>'
        '<circle cx="6" cy="12" r="3"/>'
        '<circle cx="18" cy="19" r="3"/>'
        '<path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/>'
        "</svg>"
    )


def _texto_para_js(texto):
    return json.dumps(texto).replace("</", "<\\/")


def _renderizar_botao_icone(key, titulo, icone_html, icone_confirmado_html, script_clique, cor_mutado, cor_destaque, tamanho_botao_rem):
    with st.container(key=key):
        botao_id = f"btn-{key}"
        altura = int(tamanho_botao_rem * 16)
        components.html(
            f"""
            <style>
            html, body {{ margin: 0; padding: 0; overflow: hidden; display: flex; justify-content: flex-start; }}
            #{botao_id} {{
                width: {tamanho_botao_rem}rem;
                height: {tamanho_botao_rem}rem;
                padding: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: transparent;
                color: {cor_mutado};
                border: none;
                border-radius: 50%;
                cursor: pointer;
            }}
            #{botao_id}:hover {{ color: {cor_destaque}; }}
            </style>
            <button id="{botao_id}" type="button" title="{titulo}">{icone_html}</button>
            <script>
            (function() {{
                var btn = document.getElementById("{botao_id}");
                var htmlNormal = {json.dumps(icone_html)};
                var htmlConfirmado = {json.dumps(icone_confirmado_html)};
                btn.addEventListener('click', function() {{
                    {script_clique}
                }});
            }})();
            </script>
            """,
            height=altura,
        )


def renderizar_botao_copiar(texto, key, cor_mutado, cor_destaque, tamanho_botao_rem=2.0):
    tamanho_svg = round(tamanho_botao_rem * 16 * 0.5)
    script_clique = f"""
                var texto = {_texto_para_js(texto)};
                navigator.clipboard.writeText(texto).then(function() {{
                    btn.innerHTML = htmlConfirmado;
                    setTimeout(function() {{ btn.innerHTML = htmlNormal; }}, 1500);
                }});
    """
    _renderizar_botao_icone(
        key,
        "Copiar resposta",
        _icone_copiar(tamanho_svg),
        _icone_confirmado(tamanho_svg),
        script_clique,
        cor_mutado,
        cor_destaque,
        tamanho_botao_rem,
    )


def renderizar_botao_compartilhar(texto, key, cor_mutado, cor_destaque, tamanho_botao_rem=2.0):
    tamanho_svg = round(tamanho_botao_rem * 16 * 0.5)
    script_clique = f"""
                var texto = {_texto_para_js(texto)};
                if (navigator.share) {{
                    navigator.share({{text: texto}}).catch(function() {{}});
                }} else {{
                    navigator.clipboard.writeText(texto).then(function() {{
                        btn.innerHTML = htmlConfirmado;
                        setTimeout(function() {{ btn.innerHTML = htmlNormal; }}, 1500);
                    }});
                }}
    """
    _renderizar_botao_icone(
        key,
        "Compartilhar resposta",
        _icone_compartilhar(tamanho_svg),
        _icone_confirmado(tamanho_svg),
        script_clique,
        cor_mutado,
        cor_destaque,
        tamanho_botao_rem,
    )
