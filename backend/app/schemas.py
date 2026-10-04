from typing import Literal

from pydantic import BaseModel, Field

# Limites simples para a API publica nao aceitar entradas gigantes
MAX_VERSICULOS = 40
MAX_TURNOS_HISTORICO = 20


class VersiculoEntrada(BaseModel):
    referencia: str = Field(max_length=200)
    texto: str = Field(max_length=5000)
    similaridade: float | None = None


class VersiculoSaida(VersiculoEntrada):
    # livro e capitulo permitem abrir o capitulo completo sem o cliente
    # precisar interpretar a referencia
    livro: str | None = None
    capitulo: int | None = None


class BuscaEntrada(BaseModel):
    pergunta: str = Field(min_length=2, max_length=500)


class BuscaSaida(BaseModel):
    pergunta: str
    modo: Literal["nvidia", "local"]
    resposta: str | None
    aviso: str | None
    versiculos: list[VersiculoSaida]


class RespostaEntrada(BaseModel):
    pergunta: str = Field(min_length=2, max_length=500)
    versiculos: list[VersiculoEntrada] = Field(max_length=MAX_VERSICULOS)


class RespostaSaida(BaseModel):
    resposta: str


class Turno(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatEntrada(BaseModel):
    pergunta_original: str = Field(min_length=2, max_length=500)
    resposta_original: str = Field(max_length=8000)
    versiculos: list[VersiculoEntrada] = Field(max_length=MAX_VERSICULOS)
    historico: list[Turno] = Field(default_factory=list, max_length=MAX_TURNOS_HISTORICO)
    pergunta_nova: str = Field(min_length=2, max_length=500)


class VersiculoDia(BaseModel):
    referencia: str
    texto: str
    data: str


class Livro(BaseModel):
    livro: str
    indice_inicial: int
    total_capitulos: int


class VersiculoCapitulo(BaseModel):
    versiculo: int
    texto: str


class Capitulo(BaseModel):
    livro: str
    capitulo: int
    total_capitulos_livro: int
    versiculos: list[VersiculoCapitulo]


class Saude(BaseModel):
    status: Literal["ok", "degradado"]
    nvidia_configurada: bool
    indice_nvidia: bool
    indice_local: bool
