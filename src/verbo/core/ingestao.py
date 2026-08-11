import json

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


def carregar_capitulos_para_ingestao(caminho):
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
