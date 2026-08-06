"""Cliente compartilhado para o banco vetorial Chroma."""
import chromadb

from verbo.config import CHROMA_DB_PATH, COLLECTION_NAME

_db_client: chromadb.ClientAPI | None = None


def obter_client_chroma() -> chromadb.ClientAPI:
    global _db_client
    if _db_client is None:
        _db_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return _db_client


def obter_colecao(criar_se_ausente: bool = False):
    client = obter_client_chroma()
    if criar_se_ausente:
        return client.get_or_create_collection(COLLECTION_NAME)
    return client.get_collection(COLLECTION_NAME)
