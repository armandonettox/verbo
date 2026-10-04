"""
Le biblia.json e popula o banco vetorial Chroma.
Gera dois indices na mesma pasta: o da NVIDIA (principal) e o local (fallback).

Uso:
    python scripts/construir_banco.py --indice local
    python scripts/construir_banco.py --indice nvidia
    python scripts/construir_banco.py --indice ambos

Cada indice so e criado se ainda estiver vazio. Para refazer, apague a
colecao antes (ou use --recriar).
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import chromadb
from openai import OpenAI

from verbo.config import (
    NVIDIA_API_KEY, BIBLE_JSON_PATH, CHROMA_DB_PATH,
    COLLECTION_NAME, COLLECTION_NAME_LOCAL, EMBEDDING_MODEL
)
from verbo.core.embedding_local import gerar_embeddings
from verbo.core.ingestao import carregar_capitulos_para_ingestao

BATCH_SIZE_NVIDIA = 50
BATCH_SIZE_LOCAL = 32


def _preparar_colecao(chroma, nome, recriar):
    if recriar:
        try:
            chroma.delete_collection(nome)
        except Exception:
            pass
    colecao = chroma.get_or_create_collection(nome)
    if colecao.count() > 0:
        print(f"Colecao '{nome}' ja tem {colecao.count()} itens, pulando (use --recriar).")
        return None
    return colecao


def _gravar_lote(colecao, lote, embeddings):
    colecao.add(
        ids=[v["id"] for v in lote],
        embeddings=embeddings,
        documents=[v["texto"] for v in lote],
        metadatas=[{"referencia": v["referencia"]} for v in lote],
    )


def construir_nvidia(chroma, chunks, recriar):
    colecao = _preparar_colecao(chroma, COLLECTION_NAME, recriar)
    if colecao is None:
        return

    client = OpenAI(
        api_key=NVIDIA_API_KEY,
        base_url="https://integrate.api.nvidia.com/v1",
    )
    total = len(chunks)
    for i in range(0, total, BATCH_SIZE_NVIDIA):
        lote = chunks[i:i + BATCH_SIZE_NVIDIA]
        resposta = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[v["texto"] for v in lote],
            extra_body={"input_type": "passage", "truncate": "END"},
        )
        _gravar_lote(colecao, lote, [item.embedding for item in resposta.data])
        print(f"  nvidia: {min(i + BATCH_SIZE_NVIDIA, total)}/{total}")
        time.sleep(0.5)


def construir_local(chroma, chunks, recriar):
    colecao = _preparar_colecao(chroma, COLLECTION_NAME_LOCAL, recriar)
    if colecao is None:
        return

    total = len(chunks)
    for i in range(0, total, BATCH_SIZE_LOCAL):
        lote = chunks[i:i + BATCH_SIZE_LOCAL]
        embeddings = gerar_embeddings([v["texto"] for v in lote], "passage")
        _gravar_lote(colecao, lote, embeddings)
        print(f"  local: {min(i + BATCH_SIZE_LOCAL, total)}/{total}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--indice", choices=["nvidia", "local", "ambos"], default="ambos")
    parser.add_argument("--recriar", action="store_true")
    args = parser.parse_args()

    print("Carregando e agrupando versiculos por capitulo...")
    chunks = carregar_capitulos_para_ingestao(BIBLE_JSON_PATH)
    print(f"{len(chunks)} chunks carregados.")

    chroma = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    if args.indice in ("local", "ambos"):
        construir_local(chroma, chunks, args.recriar)
    if args.indice in ("nvidia", "ambos"):
        construir_nvidia(chroma, chunks, args.recriar)

    print("Banco vetorial pronto.")


if __name__ == "__main__":
    main()
