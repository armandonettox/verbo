"""Cliente HTTP compartilhado para a API de inferencia da NVIDIA NIM.

Centraliza a instanciacao usada por busca.py, resposta.py e pelo script de
ingestao para evitar client duplicado (cada um criando o proprio OpenAI(...)).
"""
from openai import OpenAI

from verbo.config import NVIDIA_API_KEY

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

_client: OpenAI | None = None


def obter_client_nvidia() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=NVIDIA_API_KEY, base_url=NVIDIA_BASE_URL)
    return _client
