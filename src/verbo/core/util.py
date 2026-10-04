import re

TAMANHO_RESUMO_VERSICULO = 220


def resumir_texto(texto, tamanho=TAMANHO_RESUMO_VERSICULO):
    if len(texto) <= tamanho:
        return texto
    return texto[:tamanho].rsplit(" ", 1)[0] + "..."


def separar_referencia(referencia):
    """Separa 'Sao Lucas 11:1-12' em ('Sao Lucas', 11). Retorna None se o
    formato nao for reconhecido."""
    m = re.match(r"^(.+) (\d+):\d+(?:-\d+)?$", referencia)
    if not m:
        return None
    return m.group(1), int(m.group(2))


def localizar_capitulo(capitulos, referencia):
    separada = separar_referencia(referencia)
    if separada is None:
        return None
    livro, num_capitulo = separada
    for idx, capitulo in enumerate(capitulos):
        if capitulo["livro"] == livro and capitulo["capitulo"] == num_capitulo:
            return idx
    return None
