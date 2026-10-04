import datetime as dt
import logging
import os

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.app import schemas
from backend.app.dados import Biblia
from verbo.config import (
    BIBLE_JSON_PATH, COLLECTION_NAME, COLLECTION_NAME_LOCAL, NVIDIA_API_KEY
)
from verbo.core import busca
from verbo.core.erros import mensagem_erro_ia
from verbo.core.resposta import continuar_conversa, gerar_resposta
from verbo.core.util import separar_referencia
from verbo.core.versiculo_dia import obter_versiculo_do_dia

logger = logging.getLogger(__name__)

AVISO_BUSCA_LOCAL = (
    "O servico de IA esta indisponivel no momento. Mostrando uma busca "
    "simplificada, sem resposta gerada."
)
AVISO_SEM_RESULTADOS = (
    "Nenhum versiculo relevante foi encontrado para essa pergunta."
)


def _erro_ia(excecao):
    logger.warning("Falha de IA: %s", type(excecao).__name__)
    return HTTPException(status_code=503, detail=mensagem_erro_ia(excecao))


def _como_dicts(versiculos):
    return [v.model_dump() for v in versiculos]


def _versiculo_saida(versiculo):
    separada = separar_referencia(versiculo["referencia"])
    livro, capitulo = separada if separada else (None, None)
    return {**versiculo, "livro": livro, "capitulo": capitulo}


def criar_rotas():
    rotas = APIRouter(prefix="/api")

    @rotas.get("/saude", response_model=schemas.Saude)
    def saude():
        def _indice_existe(nome):
            try:
                return busca._obter_colecao(nome).count() > 0
            except Exception:
                return False

        indice_nvidia = _indice_existe(COLLECTION_NAME)
        indice_local = _indice_existe(COLLECTION_NAME_LOCAL)
        return {
            "status": "ok" if indice_local else "degradado",
            "nvidia_configurada": bool(NVIDIA_API_KEY),
            "indice_nvidia": indice_nvidia,
            "indice_local": indice_local,
        }

    @rotas.post("/buscar", response_model=schemas.BuscaSaida)
    def buscar(entrada: schemas.BuscaEntrada):
        pergunta = entrada.pergunta.strip()
        try:
            resultado = busca.buscar_com_fallback(pergunta)
        except Exception as excecao:
            raise _erro_ia(excecao)

        versiculos = resultado["versiculos"]
        modo = resultado["modo"]
        resposta = None
        aviso = None

        if modo == "local":
            aviso = AVISO_BUSCA_LOCAL
        elif not versiculos:
            aviso = AVISO_SEM_RESULTADOS
        else:
            try:
                resposta = gerar_resposta(pergunta, versiculos)
            except Exception as excecao:
                # a busca funcionou, so a resposta falhou: devolve os versiculos
                aviso = _erro_ia(excecao).detail

        return {
            "pergunta": pergunta,
            "modo": modo,
            "resposta": resposta,
            "aviso": aviso,
            "versiculos": [_versiculo_saida(v) for v in versiculos],
        }

    @rotas.post("/resposta", response_model=schemas.RespostaSaida)
    def regenerar_resposta(entrada: schemas.RespostaEntrada):
        try:
            resposta = gerar_resposta(entrada.pergunta, _como_dicts(entrada.versiculos))
        except Exception as excecao:
            raise _erro_ia(excecao)
        return {"resposta": resposta}

    @rotas.post("/chat", response_model=schemas.RespostaSaida)
    def chat(entrada: schemas.ChatEntrada):
        historico = [t.model_dump() for t in entrada.historico]
        try:
            resposta = continuar_conversa(
                entrada.pergunta_original,
                entrada.resposta_original,
                _como_dicts(entrada.versiculos),
                historico,
                entrada.pergunta_nova,
            )
        except Exception as excecao:
            raise _erro_ia(excecao)
        return {"resposta": resposta}

    return rotas


def criar_rotas_biblia():
    rotas = APIRouter(prefix="/api")

    @rotas.get("/versiculo-do-dia", response_model=schemas.VersiculoDia)
    def versiculo_do_dia(
        request: Request,
        data: dt.date | None = Query(
            default=None,
            description="Data local do usuario (AAAA-MM-DD). O servidor roda em UTC.",
        ),
    ):
        biblia = request.app.state.biblia
        item = obter_versiculo_do_dia(biblia.versiculos, data)
        return {
            "referencia": item["referencia"],
            "texto": item["texto"],
            "data": item["data"].isoformat(),
        }

    @rotas.get("/livros", response_model=list[schemas.Livro])
    def livros(request: Request):
        return request.app.state.biblia.livros

    @rotas.get("/capitulos/{livro}/{numero}", response_model=schemas.Capitulo)
    def capitulo(request: Request, livro: str, numero: int):
        resultado = request.app.state.biblia.obter_capitulo(livro, numero)
        if resultado is None:
            raise HTTPException(status_code=404, detail="Capitulo nao encontrado.")
        return resultado

    return rotas


def criar_app(caminho_biblia=None):
    app = FastAPI(title="Verbo", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.biblia = Biblia(caminho_biblia or BIBLE_JSON_PATH)

    origens = [o.strip() for o in os.getenv("VERBO_CORS_ORIGINS", "").split(",") if o.strip()]
    if origens:
        app.add_middleware(
            CORSMiddleware, allow_origins=origens, allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
        )

    app.include_router(criar_rotas())
    app.include_router(criar_rotas_biblia())
    return app
