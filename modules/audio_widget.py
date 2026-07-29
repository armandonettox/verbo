import json

import streamlit as st
import streamlit.components.v1 as components


def _icone_alto_falante(tamanho_px):
    return (
        f'<svg viewBox="0 0 24 24" width="{tamanho_px}" height="{tamanho_px}" fill="currentColor">'
        '<path d="M3 10v4h4l5 5V5L7 10H3z"/>'
        '<path d="M16.5 12c0-1.77-1-3.29-2.5-4.03v8.05c1.5-.73 2.5-2.25 2.5-4.02z"/>'
        "</svg>"
    )


def _icone_parar(tamanho_px):
    return (
        f'<svg viewBox="0 0 24 24" width="{tamanho_px}" height="{tamanho_px}" fill="currentColor">'
        '<rect x="6" y="6" width="12" height="12"/>'
        "</svg>"
    )


def _icone_tocar(tamanho_px):
    return (
        f'<svg viewBox="0 0 24 24" width="{tamanho_px}" height="{tamanho_px}" fill="currentColor">'
        '<path d="M8 5v14l11-7z"/>'
        "</svg>"
    )


def _icone_pausar(tamanho_px):
    return (
        f'<svg viewBox="0 0 24 24" width="{tamanho_px}" height="{tamanho_px}" fill="currentColor">'
        '<rect x="6" y="5" width="4" height="14"/><rect x="14" y="5" width="4" height="14"/>'
        "</svg>"
    )


def renderizar_audio(
    texto,
    key,
    cor_fundo,
    cor_texto,
    cor_mutado,
    cor_destaque,
    rotulo="Ouvir capitulo",
    icone_apenas=False,
    tamanho_botao_rem=2.75,
):
    with st.container(key=key):
        texto_audio_js = json.dumps(texto)
        botao_id = f"btn-audio-{key}"

        if icone_apenas:
            altura = int(tamanho_botao_rem * 16)
            estilo_botao = f"""
            html, body {{ display: flex; justify-content: flex-end; }}
            #ID_BOTAO {{
                width: {tamanho_botao_rem}rem;
                height: {tamanho_botao_rem}rem;
                padding: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: transparent;
                color: COR_MUTADO;
                border: none;
                border-radius: 50%;
                cursor: pointer;
            }}
            """
            tamanho_svg = round(tamanho_botao_rem * 16 * 0.59)
            conteudo_ouvir = _icone_alto_falante(tamanho_svg)
            conteudo_parar = _icone_parar(tamanho_svg)
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


def renderizar_audio_com_progresso(
    texto,
    key,
    cor_mutado,
    cor_destaque,
    tamanho_icone_rem=1.5,
    velocidade=0.95,
):
    with st.container(key=key):
        texto_audio_js = json.dumps(texto)
        botao_id = f"btn-audio-prog-{key}"
        tempo_id = f"tempo-audio-prog-{key}"

        palavras = max(len(texto.split()), 1)
        palavras_por_minuto = 155 * velocidade
        total_estimado = round(palavras / palavras_por_minuto * 60)

        tamanho_svg = round(tamanho_icone_rem * 16 * 0.6)
        icone_tocar = _icone_tocar(tamanho_svg)
        icone_pausar = _icone_pausar(tamanho_svg)

        components.html(
            (
                """
            <style>
            html, body { margin: 0; padding: 0; overflow: hidden; }
            #ID_WRAP {
                display: flex;
                align-items: center;
                gap: 0.35rem;
                font-family: "Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            #ID_BOTAO {
                width: TAMANHO_ICONErem;
                height: TAMANHO_ICONErem;
                padding: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: transparent;
                color: COR_MUTADO;
                border: none;
                border-radius: 50%;
                cursor: pointer;
                flex-shrink: 0;
            }
            #ID_BOTAO:hover { color: COR_DESTAQUE; }
            #ID_TEMPO {
                font-size: 0.72rem;
                color: COR_MUTADO;
                white-space: nowrap;
            }
            </style>
            <div id="ID_WRAP">
                <button id="ID_BOTAO" type="button" title="Ouvir capitulo">BOTAO_HTML_INICIAL</button>
                <span id="ID_TEMPO"></span>
            </div>
            <script>
            (function() {
                var btn = document.getElementById('ID_BOTAO');
                var tempoEl = document.getElementById('ID_TEMPO');
                var texto = TEXTO_JSON;
                var htmlTocar = JS_HTML_TOCAR;
                var htmlPausar = JS_HTML_PAUSAR;
                var totalEstimado = TOTAL_ESTIMADO;
                var velocidade = VELOCIDADE;
                var timerId = null;
                var elapsed = 0;

                function formatar(segundos) {
                    var s = Math.max(0, Math.round(segundos));
                    var m = Math.floor(s / 60);
                    var r = s % 60;
                    return m + ':' + (r < 10 ? '0' : '') + r;
                }

                function atualizarTempo() {
                    tempoEl.textContent = formatar(elapsed) + ' / ' + formatar(totalEstimado);
                }

                function pararTimer() {
                    if (timerId) {
                        clearInterval(timerId);
                        timerId = null;
                    }
                }

                function iniciarTimer() {
                    pararTimer();
                    timerId = setInterval(function() {
                        elapsed += 0.2;
                        atualizarTempo();
                    }, 200);
                }

                function resetar() {
                    pararTimer();
                    elapsed = 0;
                    tempoEl.textContent = '';
                    btn.innerHTML = htmlTocar;
                    btn.title = 'Ouvir capitulo';
                }

                btn.addEventListener('click', function() {
                    if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
                        window.speechSynthesis.pause();
                        pararTimer();
                        btn.innerHTML = htmlTocar;
                        btn.title = 'Continuar';
                        return;
                    }
                    if (window.speechSynthesis.paused) {
                        window.speechSynthesis.resume();
                        iniciarTimer();
                        btn.innerHTML = htmlPausar;
                        btn.title = 'Pausar';
                        return;
                    }
                    var utterance = new SpeechSynthesisUtterance(texto);
                    utterance.lang = 'pt-BR';
                    utterance.rate = velocidade;
                    utterance.onend = resetar;
                    utterance.onerror = resetar;
                    window.speechSynthesis.speak(utterance);
                    elapsed = 0;
                    atualizarTempo();
                    iniciarTimer();
                    btn.innerHTML = htmlPausar;
                    btn.title = 'Pausar';
                });
            })();
            </script>
            """
            )
            .replace("ID_WRAP", f"wrap-{botao_id}")
            .replace("ID_BOTAO", botao_id)
            .replace("ID_TEMPO", tempo_id)
            .replace("TEXTO_JSON", texto_audio_js)
            .replace("BOTAO_HTML_INICIAL", icone_tocar)
            .replace("JS_HTML_TOCAR", json.dumps(icone_tocar))
            .replace("JS_HTML_PAUSAR", json.dumps(icone_pausar))
            .replace("TOTAL_ESTIMADO", str(total_estimado))
            .replace("VELOCIDADE", str(velocidade))
            .replace("TAMANHO_ICONE", str(tamanho_icone_rem))
            .replace("COR_MUTADO", cor_mutado)
            .replace("COR_DESTAQUE", cor_destaque),
            height=int(tamanho_icone_rem * 16) + 24,
        )
