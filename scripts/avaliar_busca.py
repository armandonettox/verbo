"""
Mede a qualidade da busca com o conjunto de perguntas de tests/avaliacao/perguntas.json.
Nao roda no CI: usa os indices reais e, no indice da NVIDIA, a API (precisa da chave).

Uso:
    python scripts/avaliar_busca.py --indice local
    python scripts/avaliar_busca.py --indice nvidia
    python scripts/avaliar_busca.py --indice ambos --salvar tests/avaliacao/linha-de-base.json
    python scripts/avaliar_busca.py --indice nvidia --comparar tests/avaliacao/linha-de-base.json

O acerto em N conta se algum capitulo esperado aparece entre os N primeiros capitulos
devolvidos. O ranking e lido sem o corte de similaridade para medir a ordem; nas perguntas
fora de escopo vale a busca real, com o corte (a esperada e devolver zero versiculos).
"""
import argparse
import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from verbo.config import COLLECTION_NAME, COLLECTION_NAME_LOCAL
from verbo.core import busca
from verbo.core.avaliacao import capitulos_em_ordem, posicao_do_acerto, resumir
from verbo.core.embedding_local import gerar_embeddings

PERGUNTAS = RAIZ / "tests" / "avaliacao" / "perguntas.json"
TOTAL_LIDO = 40


def _ranking_nvidia(pergunta):
    vetor = busca._embedding_da_pergunta(pergunta)
    resultados = busca._obter_colecao(COLLECTION_NAME).query(
        query_embeddings=[vetor], n_results=TOTAL_LIDO
    )
    return busca._formatar(resultados)


def _ranking_local(pergunta):
    vetor = gerar_embeddings([pergunta], "query")[0]
    resultados = busca._obter_colecao(COLLECTION_NAME_LOCAL).query(
        query_embeddings=[vetor], n_results=TOTAL_LIDO
    )
    return busca._formatar(resultados)


def avaliar(indice, perguntas):
    ranking = _ranking_nvidia if indice == "nvidia" else _ranking_local
    itens = []
    for p in perguntas:
        inicio = time.monotonic()
        versiculos = ranking(p["pergunta"])
        segundos = time.monotonic() - inicio
        if p["esperados"]:
            posicao = posicao_do_acerto(capitulos_em_ordem(versiculos), p["esperados"])
            quantidade = len(versiculos)
        else:
            posicao = None
            # so a NVIDIA tem corte de similaridade; no local nao ha o que medir aqui
            quantidade = len(busca.buscar_versiculos(p["pergunta"])) if indice == "nvidia" else None
        itens.append({
            "id": p["id"], "categoria": p["categoria"], "pergunta": p["pergunta"],
            "esperados": p["esperados"], "posicao": posicao, "quantidade": quantidade,
            "segundos": segundos,
        })
    return itens


def _mostrar(indice, itens, resumo, anterior=None):
    print(f"\n=== Indice {indice} ===")
    for i in itens:
        if i["esperados"]:
            marca = f"#{i['posicao']}" if i["posicao"] else "nao achou"
            print(f"  {i['id']:>2} [{i['categoria']}] {marca:<10} {i['pergunta']}")
        else:
            print(f"  {i['id']:>2} [fora-de-escopo] devolveu {i['quantidade']} versiculos  {i['pergunta']}")
    print()
    for chave, valor in resumo.items():
        if chave == "por_categoria":
            for nome, dados in valor.items():
                print(f"  categoria {nome}: acerto em 10 = {dados['acerto_em_10']} ({dados['perguntas']} perguntas)")
            continue
        extra = ""
        if anterior and isinstance(valor, (int, float)) and isinstance(anterior.get(chave), (int, float)):
            extra = f"   (antes {anterior[chave]})"
        print(f"  {chave}: {valor}{extra}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--indice", choices=["nvidia", "local", "ambos"], default="ambos")
    parser.add_argument("--salvar", help="grava o resumo neste arquivo JSON")
    parser.add_argument("--comparar", help="mostra a diferenca para um resumo salvo antes")
    parser.add_argument("--so-validadas", action="store_true", help="usa so as perguntas marcadas como validadas")
    args = parser.parse_args()

    dados = json.loads(PERGUNTAS.read_text(encoding="utf-8"))
    perguntas = [p for p in dados["perguntas"] if p["validado"] or not args.so_validadas]
    anterior = json.loads(Path(args.comparar).read_text(encoding="utf-8")) if args.comparar else {}

    indices = ["nvidia", "local"] if args.indice == "ambos" else [args.indice]
    saida = {"validadas": sum(1 for p in perguntas if p["validado"]), "total": len(perguntas)}
    for indice in indices:
        itens = avaliar(indice, perguntas)
        resumo = resumir(itens)
        _mostrar(indice, itens, resumo, anterior.get(indice))
        saida[indice] = resumo

    if args.salvar:
        Path(args.salvar).write_text(json.dumps(saida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nResumo gravado em {args.salvar}")


if __name__ == "__main__":
    main()
