from verbo.core.leitura import texto_para_audio


def test_texto_para_audio_remove_marcadores_de_versiculo():
    capitulo = {
        "livro": "Genesis",
        "capitulo": 1,
        "texto": "**1.** No principio Deus criou o ceu e a terra.\n\n**2.** A terra estava vazia.",
    }
    resultado = texto_para_audio(capitulo)
    assert resultado == "No principio Deus criou o ceu e a terra. A terra estava vazia."


def test_texto_para_audio_com_um_unico_versiculo():
    capitulo = {"livro": "Teste", "capitulo": 1, "texto": "**1.** Unico versiculo."}
    resultado = texto_para_audio(capitulo)
    assert resultado == "Unico versiculo."
