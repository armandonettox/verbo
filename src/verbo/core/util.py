import re


def separar_referencia(referencia):
    """Separa 'Sao Lucas 11:1-12' em ('Sao Lucas', 11). Retorna None se o
    formato nao for reconhecido."""
    m = re.match(r"^(.+) (\d+):\d+(?:-\d+)?$", referencia)
    if not m:
        return None
    return m.group(1), int(m.group(2))
