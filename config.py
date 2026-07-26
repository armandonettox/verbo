import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Caminhos
BIBLE_JSON_PATH = "data/biblia-ave-maria.json"
CHROMA_DB_PATH = "chroma-db"
COLLECTION_NAME = "biblia"

# Modelos NVIDIA NIM (definir apos escolha no catalogo)
EMBEDDING_MODEL = "a-definir"
CHAT_MODEL = "a-definir"

# Parametros de busca
TOP_K = 5
