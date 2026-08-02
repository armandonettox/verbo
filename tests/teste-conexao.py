import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import OpenAI
from config import NVIDIA_API_KEY, EMBEDDING_MODEL

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1",
)

resposta = client.embeddings.create(
    model=EMBEDDING_MODEL,
    input=["No principio era o Verbo"],
    extra_body={"input_type": "query", "truncate": "END"},
)

print("Conexao ok, tamanho do vetor:", len(resposta.data[0].embedding))
