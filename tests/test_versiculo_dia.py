from datetime import date

from verbo.services.leitura import EPOCA
from verbo.services.plano_versiculo_dia import obter_versiculo_do_dia


def test_obter_versiculo_do_dia_retorna_versiculo_valido_na_epoca():
    resultado = obter_versiculo_do_dia(EPOCA)
    assert resultado["data"] == EPOCA
    assert resultado["referencia"]
    assert resultado["texto"]


def test_obter_versiculo_do_dia_e_deterministico_para_a_mesma_data():
    data_teste = date(2026, 3, 15)
    primeiro = obter_versiculo_do_dia(data_teste)
    segundo = obter_versiculo_do_dia(data_teste)
    assert primeiro == segundo


def test_obter_versiculo_do_dia_muda_conforme_a_data():
    resultado_um = obter_versiculo_do_dia(date(2026, 1, 1))
    resultado_dois = obter_versiculo_do_dia(date(2026, 1, 2))
    assert resultado_um["referencia"] != resultado_dois["referencia"]
