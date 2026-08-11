def listar_livros(capitulos):
    livros = []
    for idx, capitulo in enumerate(capitulos):
        if livros and livros[-1]["livro"] == capitulo["livro"]:
            livros[-1]["total_capitulos"] += 1
        else:
            livros.append({
                "livro": capitulo["livro"],
                "indice_inicial": idx,
                "total_capitulos": 1,
            })
    return livros
