from modules.plano_livre import listar_livros


def test_listar_livros_agrupa_capitulos_consecutivos_do_mesmo_livro():
    capitulos = [
        {"livro": "Genesis", "capitulo": 1, "texto": ""},
        {"livro": "Genesis", "capitulo": 2, "texto": ""},
        {"livro": "Exodo", "capitulo": 1, "texto": ""},
    ]
    livros = listar_livros(capitulos)
    assert livros == [
        {"livro": "Genesis", "indice_inicial": 0, "total_capitulos": 2},
        {"livro": "Exodo", "indice_inicial": 2, "total_capitulos": 1},
    ]
