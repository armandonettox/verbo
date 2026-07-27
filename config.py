import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Caminhos
BIBLE_JSON_PATH = "data/biblia-ave-maria.json"
CHROMA_DB_PATH = "chroma-db"
COLLECTION_NAME = "biblia"

# Modelos NVIDIA NIM
EMBEDDING_MODEL = "nvidia/nv-embedqa-e5-v5"
CHAT_MODEL = "meta/llama-3.1-8b-instruct"

# Parametros de busca
TOP_K = 8
