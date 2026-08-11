from datetime import date

from verbo.core.leitura import EPOCA
from verbo.core.versiculo_dia import obter_versiculo_do_dia

VERSICULOS = [
    {"livro": "Genesis", "capitulo": 1, "versiculo": 1, "texto": "No principio Deus criou o ceu e a terra."},
    {"livro": "Genesis", "capitulo": 1, "versiculo": 2, "texto": "A terra estava vazia."},
    {"livro": "Genesis", "capitulo": 1, "versiculo": 3, "texto": "Disse Deus: haja luz."},
    {"livro": "Exodo", "capitulo": 1, "versiculo": 1, "texto": "Estes sao os nomes dos filhos de Israel."},
]


def test_obter_versiculo_do_dia_retorna_versiculo_valido_na_epoca():
    resultado = obter_versiculo_do_dia(VERSICULOS, EPOCA)
    assert resultado["data"] == EPOCA
    assert resultado["referencia"]
    assert resultado["texto"]


def test_obter_versiculo_do_dia_e_deterministico_para_a_mesma_data():
    data_teste = date(2026, 3, 15)
    primeiro = obter_versiculo_do_dia(VERSICULOS, data_teste)
    segundo = obter_versiculo_do_dia(VERSICULOS, data_teste)
    assert primeiro == segundo


def test_obter_versiculo_do_dia_muda_conforme_a_data():
    resultado_um = obter_versiculo_do_dia(VERSICULOS, date(2026, 1, 1))
    resultado_dois = obter_versiculo_do_dia(VERSICULOS, date(2026, 1, 2))
    assert resultado_um["referencia"] != resultado_dois["referencia"]
