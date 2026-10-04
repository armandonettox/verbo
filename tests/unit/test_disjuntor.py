from verbo.core.disjuntor import Disjuntor


class _Relogio:
    def __init__(self):
        self.agora = 0.0

    def __call__(self):
        return self.agora


def _criar(falhas=2, pausa=60):
    relogio = _Relogio()
    return Disjuntor(falhas, pausa, relogio), relogio


def test_comeca_fechado_e_permite():
    disjuntor, _ = _criar()
    assert disjuntor.permite()
    assert disjuntor.estado == "fechado"


def test_uma_falha_so_nao_abre():
    disjuntor, _ = _criar(falhas=2)
    disjuntor.registrar_falha()
    assert disjuntor.permite()
    assert disjuntor.estado == "fechado"


def test_falhas_seguidas_abrem_e_bloqueiam():
    disjuntor, _ = _criar(falhas=2)
    disjuntor.registrar_falha()
    disjuntor.registrar_falha()
    assert disjuntor.estado == "aberto"
    assert not disjuntor.permite()


def test_sucesso_zera_a_contagem_de_falhas():
    disjuntor, _ = _criar(falhas=2)
    disjuntor.registrar_falha()
    disjuntor.registrar_sucesso()
    disjuntor.registrar_falha()
    assert disjuntor.estado == "fechado"


def test_continua_bloqueado_ate_o_fim_da_pausa():
    disjuntor, relogio = _criar(falhas=1, pausa=60)
    disjuntor.registrar_falha()
    relogio.agora = 59.9
    assert not disjuntor.permite()


def test_depois_da_pausa_deixa_so_uma_tentativa():
    disjuntor, relogio = _criar(falhas=1, pausa=60)
    disjuntor.registrar_falha()
    relogio.agora = 60
    assert disjuntor.estado == "testando"
    assert disjuntor.permite()
    assert not disjuntor.permite()


def test_tentativa_com_sucesso_fecha():
    disjuntor, relogio = _criar(falhas=1, pausa=60)
    disjuntor.registrar_falha()
    relogio.agora = 60
    disjuntor.permite()
    disjuntor.registrar_sucesso()
    assert disjuntor.estado == "fechado"
    assert disjuntor.permite()


def test_tentativa_com_falha_abre_de_novo_por_outra_pausa():
    disjuntor, relogio = _criar(falhas=2, pausa=60)
    disjuntor.registrar_falha()
    disjuntor.registrar_falha()
    relogio.agora = 60
    disjuntor.permite()
    disjuntor.registrar_falha()
    assert disjuntor.estado == "aberto"
    relogio.agora = 119
    assert not disjuntor.permite()
    relogio.agora = 120
    assert disjuntor.permite()
