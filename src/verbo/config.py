import os
from dotenv import load_dotenv

load_dotenv(".secrets/.env")

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Caminhos (podem ser trocados por variavel de ambiente, por exemplo
# para apontar o banco vetorial para um volume na VPS)
BIBLE_JSON_PATH = os.getenv("VERBO_BIBLE_JSON_PATH", "data/biblia.json")
CHROMA_DB_PATH = os.getenv("VERBO_CHROMA_DB_PATH", "chroma-db")
# Modelos NVIDIA NIM. A NVIDIA aposenta modelos de tempos em tempos (o e5-v5 e o
# llama-3.1-8b sairam em 2026-08-25), entao podem ser trocados por variavel de
# ambiente. Ao trocar o embedding, troque tambem o nome da colecao e reconstrua o indice.
EMBEDDING_MODEL = os.getenv("VERBO_EMBEDDING_MODEL", "nvidia/nemotron-3-embed-1b")
CHAT_MODEL = os.getenv("VERBO_CHAT_MODEL", "nvidia/nemotron-3-super-120b-a12b")
COLLECTION_NAME = os.getenv("VERBO_COLLECTION_NAME", "biblia-nemotron")
COLLECTION_NAME_LOCAL = "biblia-local"

# Embedding local (fallback quando a NVIDIA falha)
LOCAL_EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
FASTEMBED_CACHE_DIR = os.getenv("VERBO_MODELO_CACHE_DIR")  # None usa o padrao do fastembed

# Parametros de busca
TOP_K = 40
# Calibrado para o nemotron-3-embed-1b: perguntas biblicas ficam entre 30 e 66,
# perguntas fora de escopo (receita, futebol, geografia) ate 22
SIMILARIDADE_MINIMA = 28
TOP_K_LOCAL = 10
BUSCA_TIMEOUT_SEGUNDOS = float(os.getenv("VERBO_BUSCA_TIMEOUT", "8"))
CHAT_TIMEOUT_SEGUNDOS = float(os.getenv("VERBO_CHAT_TIMEOUT", "45"))

# Cache das respostas geradas (SQLite). Sem caminho, fica desligado.
CACHE_RESPOSTAS_PATH = os.getenv("VERBO_CACHE_RESPOSTAS_PATH")
CACHE_RESPOSTAS_TTL_SEGUNDOS = int(os.getenv("VERBO_CACHE_TTL_DIAS", "14")) * 86400
CACHE_RESPOSTAS_MAX_ITENS = int(os.getenv("VERBO_CACHE_MAX_ITENS", "5000"))
EMBEDDING_CACHE_ITENS = 256

# Disjuntor: depois de algumas falhas seguidas a NVIDIA e pulada por um tempo,
# para o usuario nao esperar o timeout de novo a cada busca
DISJUNTOR_FALHAS = int(os.getenv("VERBO_DISJUNTOR_FALHAS", "2"))
DISJUNTOR_PAUSA_SEGUNDOS = float(os.getenv("VERBO_DISJUNTOR_PAUSA", "60"))
