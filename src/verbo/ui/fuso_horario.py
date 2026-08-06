from datetime import datetime, timedelta

import streamlit as st
import streamlit.components.v1 as components


def agora_local():
    """Retorna o horario atual no fuso do navegador de quem esta acessando,
    usando o offset detectado via JS em garantir_data_local. Antes desse
    offset chegar, cai de volta pro horario UTC do servidor."""
    offset_minutos = st.session_state.get("tz_offset_minutos", 0)
    return datetime.utcnow() + timedelta(minutes=offset_minutos)


@st.fragment
def garantir_data_local():
    """Garante que st.session_state.data_local_usuario tenha a data de hoje no fuso
    horario do navegador de quem esta acessando. O servidor roda em UTC e nao sabe
    o fuso do usuario, entao usamos um campo escondido preenchido via JavaScript
    (o mesmo tipo de truque de manipular window.parent.document ja usado em outros
    pontos do app) em vez de navegar a pagina, que o sandbox do iframe bloqueia.

    Roda isolado num fragment para que o preenchimento do campo (disparado pelo
    JavaScript) so reexecute esse pedaco escondido, sem recarregar a pagina
    inteira e causar uma piscada visual logo na primeira carga."""
    if "data_local_usuario" in st.session_state:
        return

    with st.container(key="tz_detector"):
        offset_str = st.text_input("tz", key="tz_offset_bruto", label_visibility="collapsed")

    if offset_str:
        try:
            offset_minutos = int(offset_str)
        except ValueError:
            offset_minutos = 0
        st.session_state.tz_offset_minutos = offset_minutos
        st.session_state.data_local_usuario = agora_local().date()
        return

    # Fuso ainda nao chegou do navegador (o JS abaixo esta tentando). Quem consome
    # data_local_usuario deve usar date.today() como fallback ate a proxima rerun
    # automatica trazer o valor corrigido -- nao gravamos nada aqui de proposito,
    # senao o guard-clause do topo trava esse fallback pra sempre.
    components.html(
        """
        <script>
        (function() {
            var tentativas = 0;
            function preencher() {
                tentativas += 1;
                var doc = window.parent.document;
                var input = doc.querySelector('.st-key-tz_detector input');
                if (!input) {
                    if (tentativas < 40) setTimeout(preencher, 100);
                    return;
                }
                if (input.value) return;
                var offset = -new Date().getTimezoneOffset();
                var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                input.focus();
                setter.call(input, String(offset));
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.blur();
            }
            setTimeout(preencher, 50);
        })();
        </script>
        """,
        height=0,
    )
