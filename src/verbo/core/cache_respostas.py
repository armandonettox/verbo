import hashlib
import logging
import re
import sqlite3
import time

from verbo.config import (
    CACHE_RESPOSTAS_PATH, CACHE_RESPOSTAS_MAX_ITENS, CACHE_RESPOSTAS_TTL_SEGUNDOS,
)

logger = logging.getLogger(__name__)


def normalizar_pergunta(pergunta: str) -> str:
    """Perguntas que so mudam em caixa, espacos ou pontuacao final usam a mesma resposta."""
    texto = re.sub(r"\s+", " ", pergunta.strip().lower())
    return texto.rstrip("?!. ")


def montar_chave(modelo: str, versao_prompt: str, pergunta: str, versiculos: list[dict]) -> str:
    referencias = "|".join(v["referencia"] for v in versiculos)
    base = "\n".join([modelo, versao_prompt, normalizar_pergunta(pergunta), referencias])
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


class CacheRespostas:
    """Guarda a primeira resposta gerada para cada pergunta, em um arquivo SQLite.

    Qualquer falha do banco vira "sem cache": o cache nunca derruba a busca.
    Sem caminho configurado ele fica desligado.
    """

    def __init__(self, caminho, ttl_segundos, max_itens, relogio=time.time):
        self._caminho = caminho
        self._ttl = ttl_segundos
        self._max_itens = max_itens
        self._relogio = relogio
        self._pronto = False

    @property
    def ligado(self) -> bool:
        return bool(self._caminho)

    def _conectar(self):
        conexao = sqlite3.connect(self._caminho, timeout=2)
        if not self._pronto:
            conexao.execute(
                "CREATE TABLE IF NOT EXISTS respostas ("
                "chave TEXT PRIMARY KEY, resposta TEXT NOT NULL, criado_em REAL NOT NULL)"
            )
            conexao.commit()
            self._pronto = True
        return conexao

    def obter(self, chave: str) -> str | None:
        if not self.ligado:
            return None
        try:
            conexao = self._conectar()
            try:
                linha = conexao.execute(
                    "SELECT resposta, criado_em FROM respostas WHERE chave = ?", (chave,)
                ).fetchone()
            finally:
                conexao.close()
        except sqlite3.Error as erro:
            logger.warning("Cache de respostas indisponivel (leitura): %s", type(erro).__name__)
            return None
        if linha is None or self._relogio() - linha[1] > self._ttl:
            return None
        return linha[0]

    def guardar(self, chave: str, resposta: str):
        if not self.ligado:
            return
        agora = self._relogio()
        try:
            conexao = self._conectar()
            try:
                conexao.execute(
                    "INSERT OR REPLACE INTO respostas (chave, resposta, criado_em) VALUES (?, ?, ?)",
                    (chave, resposta, agora),
                )
                conexao.execute("DELETE FROM respostas WHERE criado_em < ?", (agora - self._ttl,))
                conexao.execute(
                    "DELETE FROM respostas WHERE chave IN ("
                    "SELECT chave FROM respostas ORDER BY criado_em DESC LIMIT -1 OFFSET ?)",
                    (self._max_itens,),
                )
                conexao.commit()
            finally:
                conexao.close()
        except sqlite3.Error as erro:
            logger.warning("Cache de respostas indisponivel (escrita): %s", type(erro).__name__)


cache = CacheRespostas(
    CACHE_RESPOSTAS_PATH, CACHE_RESPOSTAS_TTL_SEGUNDOS, CACHE_RESPOSTAS_MAX_ITENS
)
