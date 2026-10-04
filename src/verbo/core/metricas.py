import threading
from collections import defaultdict

# Contadores e latencias em memoria, zerados quando o servidor reinicia.
# Servem so para olhar a saude do app em /api/saude, sem guardar nada do usuario.
_trava = threading.Lock()
_contadores = defaultdict(int)
_latencias = defaultdict(lambda: {"quantidade": 0, "total": 0.0, "maximo": 0.0})


def contar(nome: str):
    with _trava:
        _contadores[nome] += 1


def registrar_latencia(nome: str, segundos: float):
    with _trava:
        item = _latencias[nome]
        item["quantidade"] += 1
        item["total"] += segundos
        item["maximo"] = max(item["maximo"], segundos)


def resumo() -> dict:
    with _trava:
        return {
            "contadores": dict(_contadores),
            "latencias": {
                nome: {
                    "quantidade": item["quantidade"],
                    "media_segundos": round(item["total"] / item["quantidade"], 2),
                    "maximo_segundos": round(item["maximo"], 2),
                }
                for nome, item in _latencias.items()
            },
        }


def zerar():
    with _trava:
        _contadores.clear()
        _latencias.clear()
