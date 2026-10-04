from verbo.core import metricas


def test_contar_soma():
    metricas.contar("a")
    metricas.contar("a")
    assert metricas.resumo()["contadores"] == {"a": 2}


def test_latencia_guarda_media_e_maximo():
    metricas.registrar_latencia("chat", 2.0)
    metricas.registrar_latencia("chat", 4.0)
    assert metricas.resumo()["latencias"]["chat"] == {
        "quantidade": 2, "media_segundos": 3.0, "maximo_segundos": 4.0,
    }


def test_zerar_limpa_tudo():
    metricas.contar("a")
    metricas.registrar_latencia("chat", 1.0)
    metricas.zerar()
    assert metricas.resumo() == {"contadores": {}, "latencias": {}}
