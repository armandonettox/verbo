"""Le biblia.json, gera embeddings via NVIDIA NIM e popula o banco vetorial Chroma.

Executar uma unica vez (ou apos atualizar data/biblia.json). Usa upsert, entao
rodar de novo sobre o mesmo id apenas substitui o registro em vez de duplicar.
"""
import json
import time

from verbo.config import BIBLE_JSON_PATH, EMBEDDING_MODEL
from verbo.core.chroma_client import obter_colecao
from verbo.core.nvidia_client import obter_client_nvidia

BATCH_SIZE = 50
CHUNK_SIZE = 1500


def montar_chunks_capitulo(nome_livro, num_capitulo, versiculos):
    """Agrupa versiculos de um capitulo em chunks de ate CHUNK_SIZE caracteres,
    sem quebrar versiculo no meio. Um capitulo curto vira um unico chunk."""
    chunks = []
    atual = []
    tamanho_atual = 0

    for v in versiculos:
        texto = v["texto"]
        if atual and tamanho_atual + len(texto) > CHUNK_SIZE:
            chunks.append(atual)
            atual = []
            tamanho_atual = 0
        atual.append(v)
        tamanho_atual += len(texto)

    if atual:
        chunks.append(atual)

    documentos = []
    for i, grupo in enumerate(chunks):
        primeiro = grupo[0]["versiculo"]
        ultimo = grupo[-1]["versiculo"]
        faixa = f"{primeiro}" if primeiro == ultimo else f"{primeiro}-{ultimo}"
        documentos.append({
            "id": f"{nome_livro}_{num_capitulo}_{i}",
            "texto": " ".join(v["texto"] for v in grupo),
            "referencia": f"{nome_livro} {num_capitulo}:{faixa}",
        })
    return documentos


def carregar_capitulos(caminho):
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)

    documentos = []
    for testamento_key in ["antigoTestamento", "novoTestamento"]:
        for livro in dados.get(testamento_key, []):
            nome_livro = livro["nome"]
            for capitulo in livro["capitulos"]:
                num_capitulo = capitulo["capitulo"]
                documentos.extend(
                    montar_chunks_capitulo(nome_livro, num_capitulo, capitulo["versiculos"])
                )
    return documentos


def main():
    print("Carregando e agrupando versiculos por capitulo...")
    versiculos = carregar_capitulos(BIBLE_JSON_PATH)
    total = len(versiculos)
    print(f"{total} chunks carregados.")

    client = obter_client_nvidia()
    colecao = obter_colecao(criar_se_ausente=True)

    for i in range(0, total, BATCH_SIZE):
        lote = versiculos[i:i + BATCH_SIZE]
        textos = [v["texto"] for v in lote]

        resposta = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=textos,
            extra_body={"input_type": "passage", "truncate": "END"},
        )
        embeddings = [item.embedding for item in resposta.data]

        colecao.upsert(
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
