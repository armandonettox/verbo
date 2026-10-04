import sqlite3

from verbo.core.cache_respostas import CacheRespostas, montar_chave, normalizar_pergunta

VERSICULOS = [{"referencia": "Joao 1:1"}, {"referencia": "Joao 1:2"}]


class _Relogio:
    def __init__(self):
        self.agora = 1000.0

    def __call__(self):
        return self.agora


def _cache(tmp_path, ttl=100, max_itens=3):
    relogio = _Relogio()
    return CacheRespostas(str(tmp_path / "c.sqlite"), ttl, max_itens, relogio), relogio


def test_normaliza_caixa_espacos_e_pontuacao_final():
    assert normalizar_pergunta("  O que  e a FE? ") == "o que e a fe"
    assert normalizar_pergunta("o que e a fe") == "o que e a fe"


def test_chave_igual_para_perguntas_equivalentes():
    a = montar_chave("m", "1", "O que e a fe?", VERSICULOS)
    b = montar_chave("m", "1", "o que e a fe", VERSICULOS)
    assert a == b


def test_chave_muda_com_modelo_prompt_pergunta_ou_versiculos():
    base = montar_chave("m", "1", "pergunta", VERSICULOS)
    assert montar_chave("outro", "1", "pergunta", VERSICULOS) != base
    assert montar_chave("m", "2", "pergunta", VERSICULOS) != base
    assert montar_chave("m", "1", "outra", VERSICULOS) != base
    assert montar_chave("m", "1", "pergunta", VERSICULOS[:1]) != base


def test_guarda_e_le(tmp_path):
    cache, _ = _cache(tmp_path)
    assert cache.obter("k") is None
    cache.guardar("k", "resposta")
    assert cache.obter("k") == "resposta"


def test_resposta_expira_depois_do_ttl(tmp_path):
    cache, relogio = _cache(tmp_path, ttl=100)
    cache.guardar("k", "resposta")
    relogio.agora += 100
    assert cache.obter("k") == "resposta"
    relogio.agora += 1
    assert cache.obter("k") is None


def test_respeita_o_limite_apagando_as_mais_antigas(tmp_path):
    cache, relogio = _cache(tmp_path, max_itens=3)
    for i in range(5):
        relogio.agora += 1
        cache.guardar(f"k{i}", f"r{i}")
    assert [cache.obter(f"k{i}") for i in range(5)] == [None, None, "r2", "r3", "r4"]


def test_guardar_de_novo_atualiza_o_valor(tmp_path):
    cache, relogio = _cache(tmp_path)
    cache.guardar("k", "velha")
    relogio.agora += 1
    cache.guardar("k", "nova")
    assert cache.obter("k") == "nova"


def test_sem_caminho_fica_desligado():
    cache = CacheRespostas(None, 100, 3)
    cache.guardar("k", "r")
    assert not cache.ligado
    assert cache.obter("k") is None


def test_banco_inacessivel_nao_levanta_erro(tmp_path):
    # o caminho e uma pasta, entao o SQLite nao consegue abrir
    cache = CacheRespostas(str(tmp_path), 100, 3)
    cache.guardar("k", "r")
    assert cache.obter("k") is None


def test_arquivo_corrompido_nao_levanta_erro(tmp_path):
    caminho = tmp_path / "c.sqlite"
    caminho.write_bytes(b"isto nao e um banco sqlite" * 50)
    cache = CacheRespostas(str(caminho), 100, 3)
    cache.guardar("k", "r")
    assert cache.obter("k") is None


def test_dados_persistem_entre_instancias(tmp_path):
    caminho = str(tmp_path / "c.sqlite")
    CacheRespostas(caminho, 100, 3).guardar("k", "r")
    assert CacheRespostas(caminho, 100, 3).obter("k") == "r"
    with sqlite3.connect(caminho) as conexao:
        assert conexao.execute("SELECT COUNT(*) FROM respostas").fetchone()[0] == 1
