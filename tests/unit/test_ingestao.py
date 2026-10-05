from verbo.core.ingestao import montar_chunks_capitulo


def test_montar_chunks_capitulo_agrupa_versiculos_curtos_em_um_unico_chunk():
    versiculos = [
        {"versiculo": 1, "texto": "Texto curto um."},
        {"versiculo": 2, "texto": "Texto curto dois."},
    ]
    chunks = montar_chunks_capitulo("Genesis", 1, versiculos)
    assert len(chunks) == 1
    assert chunks[0]["id"] == "Genesis_1_0"
    assert chunks[0]["referencia"] == "Genesis 1:1-2"
    assert chunks[0]["texto"] == "Texto curto um. Texto curto dois."


def test_montar_chunks_capitulo_quebra_ao_ultrapassar_o_limite():
    versiculos = [{"versiculo": i, "texto": "x" * 400} for i in range(1, 5)]
    chunks = montar_chunks_capitulo("Salmos", 119, versiculos)
    assert len(chunks) == 2
    assert chunks[0]["referencia"] == "Salmos 119:1-3"
    assert chunks[1]["referencia"] == "Salmos 119:4"


def test_montar_chunks_capitulo_nao_quebra_um_unico_versiculo_no_meio():
    versiculo_longo = "y" * 3000
    versiculos = [{"versiculo": 1, "texto": versiculo_longo}]
    chunks = montar_chunks_capitulo("Salmos", 119, versiculos)
    assert len(chunks) == 1
    assert chunks[0]["texto"] == versiculo_longo


def test_tamanho_menor_gera_mais_trechos():
    versiculos = [{"versiculo": i, "texto": "x" * 400} for i in range(1, 7)]
    grandes = montar_chunks_capitulo("Salmos", 1, versiculos)
    pequenos = montar_chunks_capitulo("Salmos", 1, versiculos, tamanho=500)
    assert len(pequenos) > len(grandes)
    assert [c["referencia"] for c in pequenos] == [f"Salmos 1:{i}" for i in range(1, 7)]


def test_com_referencia_so_muda_o_texto_do_embedding():
    versiculos = [{"versiculo": 1, "texto": "No principio."}, {"versiculo": 2, "texto": "Deus criou."}]
    simples = montar_chunks_capitulo("Gênesis", 1, versiculos)[0]
    marcado = montar_chunks_capitulo("Gênesis", 1, versiculos, com_referencia=True)[0]
    assert "texto_indexado" not in simples
    assert marcado["texto_indexado"] == "Gênesis 1:1-2. No principio. Deus criou."
    # o texto guardado e mostrado continua puro
    assert marcado["texto"] == simples["texto"] == "No principio. Deus criou."
    assert marcado["referencia"] == simples["referencia"]
