import json
from pathlib import Path

from verbo.core.avaliacao import capitulos_em_ordem, posicao_do_acerto, resumir


def _v(referencia):
    return {"referencia": referencia}


def test_capitulos_em_ordem_sem_repetir():
    versiculos = [_v("São Lucas 11:1-12"), _v("São Mateus 6:1-10"), _v("São Lucas 11:13-20")]
    assert capitulos_em_ordem(versiculos) == [("São Lucas", 11), ("São Mateus", 6)]


def test_capitulos_em_ordem_ignora_referencia_fora_do_formato():
    assert capitulos_em_ordem([_v("sem formato"), _v("Salmos 23:1-6")]) == [("Salmos", 23)]


def test_posicao_do_acerto_conta_a_partir_de_1():
    capitulos = [("A", 1), ("B", 2), ("C", 3)]
    assert posicao_do_acerto(capitulos, [["C", 3]]) == 3
    assert posicao_do_acerto(capitulos, [["C", 3], ["B", 2]]) == 2


def test_posicao_do_acerto_none_quando_nao_aparece():
    assert posicao_do_acerto([("A", 1)], [["B", 2]]) is None
    assert posicao_do_acerto([("A", 1)], [["A", 2]]) is None


def _item(posicao, categoria="conceito", esperados=(["A", 1],), quantidade=5, segundos=1.0):
    return {"categoria": categoria, "esperados": list(esperados), "posicao": posicao,
            "quantidade": quantidade, "segundos": segundos}


def test_resumir_acerto_por_corte_e_mrr():
    itens = [_item(1), _item(7), _item(30), _item(None)]
    resumo = resumir(itens)
    assert resumo["perguntas"] == 4
    assert resumo["acerto_em_5"] == 0.25
    assert resumo["acerto_em_10"] == 0.5
    assert resumo["acerto_em_40"] == 0.75
    # (1 + 1/7 + 1/30) / 4
    assert resumo["mrr"] == round((1 + 1 / 7 + 1 / 30) / 4, 3)


def test_resumir_posicao_no_limite_do_corte_conta_como_acerto():
    resumo = resumir([_item(5), _item(10), _item(40), _item(41)])
    assert resumo["acerto_em_5"] == 0.25
    assert resumo["acerto_em_10"] == 0.5
    assert resumo["acerto_em_40"] == 0.75


def test_resumir_fora_de_escopo_nao_entra_no_acerto():
    itens = [_item(1), _item(None, categoria="fora-de-escopo", esperados=(), quantidade=0),
             _item(None, categoria="fora-de-escopo", esperados=(), quantidade=3)]
    resumo = resumir(itens)
    assert resumo["perguntas"] == 1
    assert resumo["acerto_em_5"] == 1.0
    assert resumo["fora_de_escopo"] == 2
    assert resumo["fora_de_escopo_sem_versiculos"] == 0.5


def test_resumir_fora_de_escopo_sem_corte_nao_se_aplica():
    # indice local: nao ha corte de similaridade, entao a quantidade nao e medida
    itens = [_item(None, categoria="fora-de-escopo", esperados=(), quantidade=None)]
    assert resumir(itens)["fora_de_escopo_sem_versiculos"] is None


def test_resumir_por_categoria_e_tempo():
    itens = [_item(1, "conceito", segundos=1.0), _item(None, "passagem", segundos=3.0)]
    resumo = resumir(itens)
    assert resumo["por_categoria"] == {
        "conceito": {"perguntas": 1, "acerto_em_10": 1.0},
        "passagem": {"perguntas": 1, "acerto_em_10": 0.0},
    }
    assert resumo["segundos_media"] == 2.0
    assert resumo["segundos_maximo"] == 3.0


def test_resumir_sem_nenhum_item_nao_quebra():
    resumo = resumir([])
    assert resumo["perguntas"] == 0
    assert resumo["acerto_em_10"] is None


def test_arquivo_de_perguntas_esta_bem_formado():
    caminho = Path(__file__).resolve().parent.parent / "avaliacao" / "perguntas.json"
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    perguntas = dados["perguntas"]
    ids = [p["id"] for p in perguntas]
    assert len(ids) == len(set(ids)) == 30
    assert {p["categoria"] for p in perguntas} == {"conceito", "passagem", "ambigua", "fora-de-escopo"}
    for p in perguntas:
        assert len(p["pergunta"]) >= 2
        # fora de escopo nao tem capitulo esperado; as demais tem pelo menos um
        assert bool(p["esperados"]) == (p["categoria"] != "fora-de-escopo")
        for livro, capitulo in p["esperados"]:
            assert isinstance(livro, str) and isinstance(capitulo, int) and capitulo > 0


def test_capitulos_esperados_existem_na_biblia():
    raiz = Path(__file__).resolve().parent.parent.parent
    biblia = json.loads((raiz / "data" / "biblia.json").read_text(encoding="utf-8"))
    capitulos = {
        (livro["nome"], c["capitulo"])
        for parte in ("antigoTestamento", "novoTestamento")
        for livro in biblia[parte]
        for c in livro["capitulos"]
    }
    dados = json.loads((raiz / "tests" / "avaliacao" / "perguntas.json").read_text(encoding="utf-8"))
    inexistentes = [
        (p["id"], livro, capitulo)
        for p in dados["perguntas"]
        for livro, capitulo in p["esperados"]
        if (livro, capitulo) not in capitulos
    ]
    assert inexistentes == []


def test_resumir_citacoes():
    from verbo.core.avaliacao import resumir_citacoes

    itens = [
        {"citacoes": 4, "nao_confirmadas": 0},
        {"citacoes": 6, "nao_confirmadas": 2},
        {"citacoes": 0, "nao_confirmadas": 0},
        {"citacoes": 10, "nao_confirmadas": 1},
    ]
    resumo = resumir_citacoes(itens)
    assert resumo["respostas"] == 4
    assert resumo["respostas_com_citacao_nao_confirmada"] == 0.5
    assert resumo["citacoes"] == 20
    assert resumo["citacoes_nao_confirmadas"] == 3
    assert resumo["taxa_citacao_nao_confirmada"] == 0.15


def test_resumir_citacoes_sem_respostas_nem_citacoes():
    from verbo.core.avaliacao import resumir_citacoes

    assert resumir_citacoes([])["respostas_com_citacao_nao_confirmada"] is None
    assert resumir_citacoes([{"citacoes": 0, "nao_confirmadas": 0}])["taxa_citacao_nao_confirmada"] is None


def test_resumir_margem_do_corte_de_similaridade():
    itens = [
        _item(1) | {"similaridade_top": 48.0},
        _item(3) | {"similaridade_top": 33.5},
        _item(None, categoria="fora-de-escopo", esperados=(), quantidade=0) | {"similaridade_top": 23.2},
        _item(None, categoria="fora-de-escopo", esperados=(), quantidade=0) | {"similaridade_top": 14.0},
    ]
    resumo = resumir(itens)
    assert resumo["em_escopo_menor_similaridade"] == 33.5
    assert resumo["fora_de_escopo_maior_similaridade"] == 23.2
    assert resumo["em_escopo_sem_versiculos"] == 0


def test_resumir_conta_pergunta_em_escopo_que_o_corte_deixaria_sem_versiculos():
    itens = [_item(None, quantidade=0) | {"similaridade_top": 20.0}, _item(1) | {"similaridade_top": 40.0}]
    assert resumir(itens)["em_escopo_sem_versiculos"] == 1


def test_resumir_sem_similaridade_nao_inventa_margem():
    # indice local: sem notas de similaridade
    resumo = resumir([_item(1)])
    assert resumo["em_escopo_menor_similaridade"] is None
    assert resumo["fora_de_escopo_maior_similaridade"] is None
    assert resumo["em_escopo_sem_versiculos"] is None
