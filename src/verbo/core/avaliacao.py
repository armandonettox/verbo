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
    # margem do corte de similaridade (so a NVIDIA): a maior nota de uma pergunta fora de escopo
    # precisa ficar abaixo do corte, e a menor de uma pergunta em escopo, acima
    dentro = [i["similaridade_top"] for i in com_resposta if i.get("similaridade_top") is not None]
    fora_notas = [i["similaridade_top"] for i in fora if i.get("similaridade_top") is not None]
    resumo["em_escopo_menor_similaridade"] = min(dentro) if dentro else None
    resumo["fora_de_escopo_maior_similaridade"] = max(fora_notas) if fora_notas else None
    resumo["em_escopo_sem_versiculos"] = (
        sum(1 for i in com_resposta if i["quantidade"] == 0) if dentro else None
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


def resumir_citacoes(itens: list[dict]) -> dict:
    """Resume a conferencia das citacoes das respostas geradas.

    Cada item tem citacoes (quantidade de capitulos citados) e nao_confirmadas (quantos
    deles nao estavam entre os versiculos enviados ao LLM)."""
    total = sum(i["citacoes"] for i in itens)
    fora = sum(i["nao_confirmadas"] for i in itens)
    return {
        "respostas": len(itens),
        "respostas_com_citacao_nao_confirmada": (
            round(sum(1 for i in itens if i["nao_confirmadas"]) / len(itens), 3) if itens else None
        ),
        "citacoes": total,
        "citacoes_nao_confirmadas": fora,
        "taxa_citacao_nao_confirmada": round(fora / total, 3) if total else None,
    }
