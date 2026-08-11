"""
Le biblia.json, gera embeddings via NVIDIA NIM
e popula o banco vetorial Chroma. Executar uma unica vez.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import chromadb
from openai import OpenAI

from verbo.config import (
    NVIDIA_API_KEY, BIBLE_JSON_PATH, CHROMA_DB_PATH,
    COLLECTION_NAME, EMBEDDING_MODEL
)
from verbo.core.ingestao import carregar_capitulos_para_ingestao

BATCH_SIZE = 50


def main():
    print("Carregando e agrupando versiculos por capitulo...")
    versiculos = carregar_capitulos_para_ingestao(BIBLE_JSON_PATH)
    total = len(versiculos)
    print(f"{total} chunks carregados.")

    client = OpenAI(
        api_key=NVIDIA_API_KEY,
        base_url="https://integrate.api.nvidia.com/v1",
    )

    chroma = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    colecao = chroma.get_or_create_collection(COLLECTION_NAME)

    for i in range(0, total, BATCH_SIZE):
        lote = versiculos[i:i + BATCH_SIZE]
        textos = [v["texto"] for v in lote]

        resposta = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=textos,
            extra_body={"input_type": "passage", "truncate": "END"},
        )
        embeddings = [item.embedding for item in resposta.data]

        colecao.add(
            ids=[v["id"] for v in lote],
            embeddings=embeddings,
            documents=textos,
            metadatas=[{"referencia": v["referencia"]} for v in lote],
        )

        processados = min(i + BATCH_SIZE, total)
        print(f"  {processados}/{total} processados...")
        time.sleep(0.5)

    print("Banco vetorial construido.")


if __name__ == "__main__":
    main()
