import os
from dotenv import load_dotenv

load_dotenv(".secrets/.env")

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

if not NVIDIA_API_KEY:
    try:
        import streamlit as st
        NVIDIA_API_KEY = st.secrets.get("NVIDIA_API_KEY")
    except Exception:
        pass

# Caminhos
BIBLE_JSON_PATH = "data/biblia.json"
CHROMA_DB_PATH = "chroma-db"
COLLECTION_NAME = "biblia"

# Modelos NVIDIA NIM
EMBEDDING_MODEL = "nvidia/nv-embedqa-e5-v5"
CHAT_MODEL = "meta/llama-3.1-8b-instruct"

# Parametros de busca
TOP_K = 40
SIMILARIDADE_MINIMA = 40
