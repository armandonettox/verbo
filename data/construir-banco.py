"""
Le biblia-ave-maria.json, gera embeddings via NVIDIA NIM
e popula o banco vetorial Chroma. Executar uma unica vez.
"""
import json
import time
import chromadb
from openai import OpenAI
from config import (
    NVIDIA_API_KEY, BIBLE_JSON_PATH, CHROMA_DB_PATH,
    COLLECTION_NAME, EMBEDDING_MODEL
)

BATCH_SIZE = 50


def carregar_versiculos(caminho):
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)

    versiculos = []
    for testamento_key in ["antigoTestamento", "novoTestamento"]:
        for livro in dados.get(testamento_key, []):
            nome_livro = livro["nome"]
            for capitulo in livro["capitulos"]:
                num_capitulo = capitulo["capitulo"]
                for v in capitulo["versiculos"]:
                    versiculos.append({
                        "id": f"{nome_livro}_{num_capitulo}_{v['versiculo']}",
                        "texto": v["texto"],
                        "referencia": f"{nome_livro} {num_capitulo}:{v['versiculo']}",
                    })
    return versiculos


def main():
    print("Carregando versiculos...")
    versiculos = carregar_versiculos(BIBLE_JSON_PATH)
    total = len(versiculos)
    print(f"{total} versiculos carregados.")

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
