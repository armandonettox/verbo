from verbo.core.util import separar_referencia

# Posicoes em que o acerto e contado (o site manda ate 40 trechos ao LLM)
CORTES = (5, 10, 40)


def capitulos_em_ordem(versiculos: list[dict]) -> list[tuple[str, int]]:
    """Lista os capitulos dos resultados na ordem de relevancia, sem repetir.
    O indice guarda um trecho por capitulo, entao o acerto e medido por capitulo."""
    vistos = []
    for v in versiculos:
        capitulo = separar_referencia(v["referencia"])
        if capitulo and capitulo not in vistos:
            vistos.append(capitulo)
    return vistos


def posicao_do_acerto(capitulos: list[tuple[str, int]], esperados: list) -> int | None:
    """Posicao (a partir de 1) do primeiro capitulo esperado, ou None se nenhum apareceu."""
    esperados = {(livro, capitulo) for livro, capitulo in esperados}
    for posicao, capitulo in enumerate(capitulos, start=1):
        if capitulo in esperados:
            return posicao
    return None


def resumir(itens: list[dict]) -> dict:
    """Resume os resultados de uma rodada.

    Cada item tem categoria, esperados, posicao (do primeiro acerto, ou None),
    quantidade (de versiculos devolvidos pela busca real) e segundos.
    Perguntas fora de escopo nao entram no acerto: o que se mede nelas e se a busca
    devolveu zero versiculos."""
    com_resposta = [i for i in itens if i["esperados"]]
    fora = [i for i in itens if not i["esperados"]]

    resumo = {"perguntas": len(com_resposta)}
    for corte in CORTES:
        acertos = sum(1 for i in com_resposta if i["posicao"] is not None and i["posicao"] <= corte)
        resumo[f"acerto_em_{corte}"] = round(acertos / len(com_resposta), 3) if com_resposta else None
    resumo["mrr"] = (
        round(sum(1 / i["posicao"] for i in com_resposta if i["posicao"]) / len(com_resposta), 3)
        if com_resposta else None
    )
    resumo["fora_de_escopo"] = len(fora)
    # quantidade None = a busca nao tem corte de similaridade (indice local): nao se aplica
    medidas = [i for i in fora if i["quantidade"] is not None]
    resumo["fora_de_escopo_sem_versiculos"] = (
        round(sum(1 for i in medidas if i["quantidade"] == 0) / len(medidas), 3) if medidas else None
    )
    por_categoria = {}
    for categoria in sorted({i["categoria"] for i in com_resposta}):
        grupo = [i for i in com_resposta if i["categoria"] == categoria]
        por_categoria[categoria] = {
            "perguntas": len(grupo),
            "acerto_em_10": round(
                sum(1 for i in grupo if i["posicao"] is not None and i["posicao"] <= 10) / len(grupo), 3
            ),
        }
    resumo["por_categoria"] = por_categoria
    tempos = sorted(i["segundos"] for i in itens)
    resumo["segundos_media"] = round(sum(tempos) / len(tempos), 2) if tempos else None
    resumo["segundos_maximo"] = round(tempos[-1], 2) if tempos else None
    return resumo
