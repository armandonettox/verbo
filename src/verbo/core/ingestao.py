import json

CHUNK_SIZE = 1500


def montar_chunks_capitulo(nome_livro, num_capitulo, versiculos, tamanho=CHUNK_SIZE, com_referencia=False):
    """Agrupa versiculos de um capitulo em chunks de ate `tamanho` caracteres,
    sem quebrar versiculo no meio. Um capitulo curto vira um unico chunk.

    Com `com_referencia`, cada chunk ganha `texto_indexado`: o texto com a referencia na
    frente, usado so para gerar o embedding (o texto guardado e mostrado continua puro)."""
    chunks = []
    atual = []
    tamanho_atual = 0

    for v in versiculos:
        texto = v["texto"]
        if atual and tamanho_atual + len(texto) > tamanho:
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
        documento = {
            "id": f"{nome_livro}_{num_capitulo}_{i}",
            "texto": " ".join(v["texto"] for v in grupo),
            "referencia": f"{nome_livro} {num_capitulo}:{faixa}",
        }
        if com_referencia:
            documento["texto_indexado"] = f"{documento['referencia']}. {documento['texto']}"
        documentos.append(documento)
    return documentos


def carregar_capitulos_para_ingestao(caminho, tamanho=CHUNK_SIZE, com_referencia=False):
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)

    documentos = []
    for testamento_key in ["antigoTestamento", "novoTestamento"]:
        for livro in dados.get(testamento_key, []):
            nome_livro = livro["nome"]
            for capitulo in livro["capitulos"]:
                num_capitulo = capitulo["capitulo"]
                documentos.extend(
                    montar_chunks_capitulo(
                        nome_livro, num_capitulo, capitulo["versiculos"], tamanho, com_referencia
                    )
                )
    return documentos
