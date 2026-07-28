import json

import streamlit as st
import streamlit.components.v1 as components


def renderizar_audio(texto, key, cor_fundo, cor_texto, cor_mutado, cor_destaque, rotulo="Ouvir capitulo"):
    with st.container(key=key):
        texto_audio_js = json.dumps(texto)
        botao_id = f"btn-audio-{key}"
        components.html(
            """
            <style>
            html, body { margin: 0; padding: 0; overflow: hidden; }
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
            #ID_BOTAO:hover {
                border-color: COR_DESTAQUE;
                color: COR_DESTAQUE;
            }
            </style>
            <button id="ID_BOTAO" type="button">ROTULO_INICIAL</button>
            <script>
            (function() {
                var btn = document.getElementById('ID_BOTAO');
                var texto = TEXTO_JSON;
                var ROTULO_OUVIR = 'ROTULO_INICIAL';
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
            .replace("ID_BOTAO", botao_id)
            .replace("TEXTO_JSON", texto_audio_js)
            .replace("ROTULO_INICIAL", rotulo)
            .replace("COR_FUNDO", cor_fundo)
            .replace("COR_TEXTO", cor_texto)
            .replace("COR_MUTADO", cor_mutado)
            .replace("COR_DESTAQUE", cor_destaque),
            height=40,
        )
