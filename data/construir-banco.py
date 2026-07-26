"""
Le biblia-ave-maria.json, gera embeddings via NVIDIA NIM
e popula o banco vetorial Chroma. Executar uma unica vez.
"""
import json
import chromadb
from openai import OpenAI
from config import (
    NVIDIA_API_KEY, BIBLE_JSON_PATH, CHROMA_DB_PATH,
    COLLECTION_NAME, EMBEDDING_MODEL
)


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


def gerar_embedding(client, texto):
    resposta = client.embeddings.create(model=EMBEDDING_MODEL, input=texto)
    return resposta.data[0].embedding


def main():
    print("Carregando versiculos...")
    versiculos = carregar_versiculos(BIBLE_JSON_PATH)
    print(f"{len(versiculos)} versiculos carregados.")

    client = OpenAI(
        api_key=NVIDIA_API_KEY,
        base_url="https://integrate.api.nvidia.com/v1",
    )

    chroma = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    colecao = chroma.get_or_create_collection(COLLECTION_NAME)

    # TODO: processar em lotes para respeitar rate limit da NVIDIA NIM
    for i, v in enumerate(versiculos):
        embedding = gerar_embedding(client, v["texto"])
        colecao.add(
            ids=[v["id"]],
            embeddings=[embedding],
            documents=[v["texto"]],
            metadatas=[{"referencia": v["referencia"]}],
        )
        if i % 500 == 0:
            print(f"  {i}/{len(versiculos)} processados...")

    print("Banco vetorial construido.")


if __name__ == "__main__":
    main()
