import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

# No Streamlit Cloud a chave vem de st.secrets. O core so le variavel de
# ambiente, entao copiamos antes de importar qualquer modulo do projeto.
if not os.getenv("NVIDIA_API_KEY"):
    try:
        import streamlit as st
        os.environ["NVIDIA_API_KEY"] = st.secrets.get("NVIDIA_API_KEY") or ""
    except Exception:
        pass

from verbo.ui.pagina import render

render()
