import json

import streamlit as st
import streamlit.components.v1 as components


ICONE_ALTO_FALANTE = (
    '<svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor">'
    '<path d="M3 10v4h4l5 5V5L7 10H3z"/>'
    '<path d="M16.5 12c0-1.77-1-3.29-2.5-4.03v8.05c1.5-.73 2.5-2.25 2.5-4.02z"/>'
    "</svg>"
)
ICONE_PARAR = (
    '<svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor">'
    '<rect x="6" y="6" width="12" height="12"/>'
    "</svg>"
)


def renderizar_audio(
    texto, key, cor_fundo, cor_texto, cor_mutado, cor_destaque, rotulo="Ouvir capitulo", icone_apenas=False
):
    with st.container(key=key):
        texto_audio_js = json.dumps(texto)
        botao_id = f"btn-audio-{key}"

        if icone_apenas:
            estilo_botao = """
            html, body { display: flex; justify-content: flex-end; }
            #ID_BOTAO {
                width: 2.75rem;
                height: 2.75rem;
                padding: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: transparent;
                color: COR_MUTADO;
                border: none;
                border-radius: 50%;
                cursor: pointer;
            }
            """
            conteudo_ouvir = ICONE_ALTO_FALANTE
            conteudo_parar = ICONE_PARAR
            altura = 44
        else:
            estilo_botao = """
            #ID_BOTAO {
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
            """
            conteudo_ouvir = rotulo
            conteudo_parar = "Parar audio"
            altura = 40

        components.html(
            (
                """
            <style>
            html, body { margin: 0; padding: 0; overflow: hidden; }
            """
                + estilo_botao
                + """
            #ID_BOTAO:hover {
                border-color: COR_DESTAQUE;
                color: COR_DESTAQUE;
            }
            </style>
            <button id="ID_BOTAO" type="button" title="Ouvir leitura">BOTAO_HTML_INICIAL</button>
            <script>
            (function() {
                var btn = document.getElementById('ID_BOTAO');
                var texto = TEXTO_JSON;
                var htmlOuvir = JS_HTML_OUVIR;
                var htmlParar = JS_HTML_PARAR;
                btn.innerHTML = htmlOuvir;

                btn.addEventListener('click', function() {
                    if (window.speechSynthesis.speaking) {
                        window.speechSynthesis.cancel();
                        btn.innerHTML = htmlOuvir;
                        return;
                    }
                    var utterance = new SpeechSynthesisUtterance(texto);
                    utterance.lang = 'pt-BR';
                    utterance.rate = 0.95;
                    utterance.onend = function() { btn.innerHTML = htmlOuvir; };
                    utterance.onerror = function() { btn.innerHTML = htmlOuvir; };
                    window.speechSynthesis.speak(utterance);
                    btn.innerHTML = htmlParar;
                });
            })();
            </script>
            """
            )
            .replace("ID_BOTAO", botao_id)
            .replace("TEXTO_JSON", texto_audio_js)
            .replace("BOTAO_HTML_INICIAL", conteudo_ouvir)
            .replace("JS_HTML_OUVIR", json.dumps(conteudo_ouvir))
            .replace("JS_HTML_PARAR", json.dumps(conteudo_parar))
            .replace("COR_FUNDO", cor_fundo)
            .replace("COR_TEXTO", cor_texto)
            .replace("COR_MUTADO", cor_mutado)
            .replace("COR_DESTAQUE", cor_destaque),
            height=altura,
        )
