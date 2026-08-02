import importlib.util
from pathlib import Path

_CAMINHO = Path(__file__).resolve().parent.parent / "data" / "construir-banco.py"
_spec = importlib.util.spec_from_file_location("construir_banco", _CAMINHO)
construir_banco = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(construir_banco)

montar_chunks_capitulo = construir_banco.montar_chunks_capitulo


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
