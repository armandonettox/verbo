import threading
import time


class Disjuntor:
    """Pula um servico que esta falhando por um tempo.

    Fechado: tudo passa. Depois de `falhas_para_abrir` falhas seguidas ele abre
    e bloqueia por `pausa_segundos`. Passada a pausa, deixa uma unica tentativa
    de teste: se der certo fecha, se falhar abre de novo.
    """

    def __init__(self, falhas_para_abrir, pausa_segundos, relogio=time.monotonic):
        self._falhas_para_abrir = falhas_para_abrir
        self._pausa = pausa_segundos
        self._relogio = relogio
        self._trava = threading.Lock()
        self._falhas = 0
        self._aberto_ate = None
        self._testando = False

    def permite(self) -> bool:
        with self._trava:
            if self._aberto_ate is None:
                return True
            if self._testando or self._relogio() < self._aberto_ate:
                return False
            self._testando = True
            return True

    def registrar_sucesso(self):
        with self._trava:
            self._falhas = 0
            self._aberto_ate = None
            self._testando = False

    def registrar_falha(self):
        with self._trava:
            self._falhas += 1
            if self._testando or self._falhas >= self._falhas_para_abrir:
                self._aberto_ate = self._relogio() + self._pausa
                self._testando = False

    @property
    def estado(self) -> str:
        with self._trava:
            if self._aberto_ate is None:
                return "fechado"
            if self._testando or self._relogio() >= self._aberto_ate:
                return "testando"
            return "aberto"
