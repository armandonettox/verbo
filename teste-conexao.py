import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
)

resposta = client.embeddings.create(
    model="nvidia/nv-embedqa-e5-v5",
    input=["No principio era o Verbo"],
    extra_body={"input_type": "query", "truncate": "END"},
)

print("Conexao ok, tamanho do vetor:", len(resposta.data[0].embedding))
