import pytest

from verbo.core.citacoes import LIVROS, citacoes_na_resposta, nao_confirmadas

# o LLM escreve as faixas de versiculos com o hifen nao separavel
NBH = chr(0x2011)


def _versiculos(*referencias):
    return [{"referencia": r, "texto": "x"} for r in referencias]


def test_le_citacao_com_dois_pontos_e_faixa():
    texto = f"Jesus ensinou o Pai Nosso (Lucas 11:2{NBH}4) e a persistencia (Lucas 18:1{NBH}8)."
    assert citacoes_na_resposta(texto) == [("São Lucas", 11), ("São Lucas", 18)]


def test_nao_repete_o_mesmo_capitulo():
    texto = "Lucas 11:2-4, depois Lucas 11:9-10 e de novo Lucas 11:5."
    assert citacoes_na_resposta(texto) == [("São Lucas", 11)]


def test_livros_com_numeral_romano_e_arabico():
    assert citacoes_na_resposta("II Coríntios 1:1-10") == [("II Coríntios", 1)]
    assert citacoes_na_resposta("2 Coríntios 1:1") == [("II Coríntios", 1)]
    assert citacoes_na_resposta("1 Coríntios 13:4") == [("I Coríntios", 13)]
    assert citacoes_na_resposta("I São Pedro 4:13") == [("I São Pedro", 4)]
    assert citacoes_na_resposta("1 Pedro 4:13") == [("I São Pedro", 4)]
    assert citacoes_na_resposta("1º Samuel 17:45") == [("I Samuel", 17)]


def test_joao_e_as_cartas_de_joao_nao_se_confundem():
    assert citacoes_na_resposta("João 3:16") == [("São João", 3)]
    assert citacoes_na_resposta("1 João 4:8") == [("I São João", 4)]
    assert citacoes_na_resposta("III João 1:4") == [("III São João", 1)]


def test_nome_com_ou_sem_sao_e_sem_acento():
    assert citacoes_na_resposta("São Mateus 5:44") == [("São Mateus", 5)]
    assert citacoes_na_resposta("Mateus 5:44") == [("São Mateus", 5)]
    assert citacoes_na_resposta("MATEUS 5:44") == [("São Mateus", 5)]
    assert citacoes_na_resposta("Genesis 1:1") == [("Gênesis", 1)]
    assert citacoes_na_resposta("Proverbios 3:5") == [("Provérbios", 3)]


def test_variantes_de_nomes():
    assert citacoes_na_resposta("Atos 2:1") == [("Atos dos Apóstolos", 2)]
    assert citacoes_na_resposta("Salmo 23:1") == [("Salmos", 23)]
    assert citacoes_na_resposta("Salmos 23") == [("Salmos", 23)]
    assert citacoes_na_resposta("Cantares 2:1") == [("Cântico dos Cânticos", 2)]


def test_citacao_so_com_capitulo():
    assert citacoes_na_resposta("veja Romanos 8 inteiro") == [("Romanos", 8)]


def test_trecho_sem_nome_de_livro_nao_e_lido():
    # numa lista de referencias o LLM omite o livro repetido
    texto = f"Referencias: Lucas 11:2{NBH}4, 11:5{NBH}8, 11:9{NBH}10; Marcos 11:24."
    assert citacoes_na_resposta(texto) == [("São Lucas", 11), ("São Marcos", 11)]


def test_palavra_comum_sem_numero_nao_vira_citacao():
    assert citacoes_na_resposta("Jonas foi ao mar e Ester foi rainha. Tito e Rute.") == []


def test_nome_dentro_de_outra_palavra_nao_conta():
    assert citacoes_na_resposta("Isaiasx 5 e xRomanos 8") == []


def test_cada_livro_e_reconhecido_pelo_proprio_nome():
    for nome in LIVROS:
        assert citacoes_na_resposta(f"{nome} 7:1") == [(nome, 7)], nome


def test_nao_confirmadas_aponta_o_que_nao_foi_enviado():
    versiculos = _versiculos("São Lucas 11:1-12", "São Mateus 6:1-10")
    texto = "Lucas 11:2-4 e Mateus 6:9 estao ok, mas Mateus 7:7 e Joao 3:16 nao estavam."
    assert nao_confirmadas(texto, versiculos) == ["São Mateus 7", "São João 3"]


def test_nao_confirmadas_vazio_quando_tudo_foi_enviado():
    versiculos = _versiculos("São Lucas 11:1-12", "São Lucas 11:13-20")
    assert nao_confirmadas("Lucas 11:2 e Lucas 11:15", versiculos) == []


def test_resposta_sem_citacao_nao_gera_alerta():
    assert nao_confirmadas("Nenhum versiculo responde a pergunta.", _versiculos("São Lucas 11:1-12")) == []


def test_mesmo_capitulo_de_livro_diferente_nao_confirma():
    versiculos = _versiculos("São João 3:1-12")
    assert nao_confirmadas("I São João 3:1", versiculos) == ["I São João 3"]


@pytest.mark.parametrize("referencia", ["sem formato", "", "Lucas"])
def test_referencia_fora_do_formato_nao_quebra(referencia):
    assert nao_confirmadas("Lucas 11:1", _versiculos(referencia)) == ["São Lucas 11"]


def test_resposta_real_do_llm_sobre_sofrimento():
    # trecho de uma resposta real do site (2026-10-05), com os hifens nao separaveis
    texto = (
        f"- **Prova e fidelidade** - (Judite 8:22{NBH}32).\n"
        f"- **Disciplina** - (Eclesiastico 2:1{NBH}13). Ele tambem corrige (Sabedoria 11:1{NBH}14).\n"
        f"- **Dependencia** - (II Corintios 1:1{NBH}10) e (I Sao Pedro 4:13{NBH}19; Eclesiastico 2:1{NBH}13).\n"
        f"- **Justica** - (Jo 36:1{NBH}19), (Deuteronomio 4:30{NBH}38), (Romanos 8:26{NBH}37; Romanos 9:15{NBH}27)."
    )
    assert citacoes_na_resposta(texto) == [
        ("Judite", 8), ("Eclesiástico", 2), ("Sabedoria", 11), ("II Coríntios", 1),
        ("I São Pedro", 4), ("Jó", 36), ("Deuteronômio", 4), ("Romanos", 8), ("Romanos", 9),
    ]


def test_numero_maior_que_um_capitulo_nao_vira_citacao():
    # anos e quantidades depois de um nome de livro nao sao capitulos
    assert citacoes_na_resposta("Daniel 2024 e Rute 1234") == []
