import datetime as dt
import logging
import os
import threading

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.app import schemas
from backend.app.dados import Biblia
from verbo.config import (
    BIBLE_JSON_PATH, CHAT_MODEL, COLLECTION_NAME, COLLECTION_NAME_LOCAL, NVIDIA_API_KEY
)
from verbo.core import embedding_local, busca, metricas, resposta as modulo_resposta
from verbo.core.cache_respostas import cache as cache_respostas, montar_chave
from verbo.core.erros import IAInstavelError, mensagem_erro_ia
from verbo.core.resposta import PROMPT_VERSAO, continuar_conversa, gerar_resposta
from verbo.core.util import separar_referencia
from verbo.core.versiculo_dia import obter_versiculo_do_dia

logger = logging.getLogger(__name__)

AVISO_BUSCA_LOCAL = (
    "O servico de IA esta indisponivel no momento. Mostrando uma busca "
    "simplificada, sem resposta gerada."
)
# O texto da Biblia nao muda, entao navegador e CDN podem guardar por um dia
CACHE_TEXTO_BIBLICO = "public, max-age=86400"
CACHE_VERSICULO_DO_DIA = "public, max-age=3600"

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


def _resposta_com_cache(pergunta, versiculos):
    chave = montar_chave(CHAT_MODEL, PROMPT_VERSAO, pergunta, versiculos)
    guardada = cache_respostas.obter(chave)
    if guardada is not None:
        metricas.contar("resposta_cache_acerto")
        return guardada
    metricas.contar("resposta_cache_falha")
    resposta = gerar_resposta(pergunta, versiculos)
    if resposta:
        cache_respostas.guardar(chave, resposta)
    return resposta


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
            "disjuntor_busca": busca.disjuntor.estado,
            "disjuntor_chat": modulo_resposta.disjuntor.estado,
            "metricas": metricas.resumo(),
        }

    @rotas.post("/versiculos", response_model=schemas.VersiculosSaida)
    def versiculos(entrada: schemas.BuscaEntrada):
        pergunta = entrada.pergunta.strip()
        try:
            resultado = busca.buscar_com_fallback(pergunta)
        except Exception as excecao:
            raise _erro_ia(excecao)

        aviso = None
        if resultado["modo"] == "local":
            aviso = AVISO_BUSCA_LOCAL
        elif not resultado["versiculos"]:
            aviso = AVISO_SEM_RESULTADOS

        return {
            "pergunta": pergunta,
            "modo": resultado["modo"],
            "aviso": aviso,
            "versiculos": [_versiculo_saida(v) for v in resultado["versiculos"]],
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
                resposta = _resposta_com_cache(pergunta, versiculos)
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
        versiculos = _como_dicts(entrada.versiculos)
        try:
            if entrada.usar_cache:
                resposta = _resposta_com_cache(entrada.pergunta, versiculos)
            else:
                resposta = gerar_resposta(entrada.pergunta, versiculos)
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
        response: Response,
        data: dt.date | None = Query(
            default=None,
            description="Data local do usuario (AAAA-MM-DD). O servidor roda em UTC.",
        ),
    ):
        # sem data o resultado depende do dia do servidor, entao nao pode ser guardado
        response.headers["Cache-Control"] = CACHE_VERSICULO_DO_DIA if data else "no-cache"
        biblia = request.app.state.biblia
        item = obter_versiculo_do_dia(biblia.versiculos, data)
        return {
            "referencia": item["referencia"],
            "texto": item["texto"],
            "data": item["data"].isoformat(),
        }

    @rotas.get("/livros", response_model=list[schemas.Livro])
    def livros(request: Request, response: Response):
        response.headers["Cache-Control"] = CACHE_TEXTO_BIBLICO
        return request.app.state.biblia.livros

    @rotas.get("/capitulos/{livro}/{numero}", response_model=schemas.Capitulo)
    def capitulo(request: Request, response: Response, livro: str, numero: int):
        resultado = request.app.state.biblia.obter_capitulo(livro, numero)
        if resultado is None:
            raise HTTPException(status_code=404, detail="Capitulo nao encontrado.")
        response.headers["Cache-Control"] = CACHE_TEXTO_BIBLICO
        return resultado

    return rotas


def _aquecer_modelo_local():
    # A primeira busca local baixaria e carregaria o modelo (~50 s). Fazendo isso
    # ao iniciar, em segundo plano, o fallback ja nasce pronto.
    try:
        embedding_local.gerar_embeddings(["aquecimento"], "query")
        logger.info("Modelo local carregado")
    except Exception as erro:
        logger.warning("Nao foi possivel carregar o modelo local: %s", type(erro).__name__)


def criar_app(caminho_biblia=None):
    app = FastAPI(title="Verbo", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.biblia = Biblia(caminho_biblia or BIBLE_JSON_PATH)

    origens = [o.strip() for o in os.getenv("VERBO_CORS_ORIGINS", "").split(",") if o.strip()]
    if origens:
        app.add_middleware(
            CORSMiddleware, allow_origins=origens, allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
        )

    @app.middleware("http")
    async def nao_guardar_posts(request: Request, call_next):
        # perguntas e respostas nunca devem ficar no navegador nem em CDN
        resposta = await call_next(request)
        if request.method == "POST":
            resposta.headers["Cache-Control"] = "no-store"
        return resposta

    app.include_router(criar_rotas())
    app.include_router(criar_rotas_biblia())

    if os.getenv("VERBO_AQUECER_MODELO_LOCAL") == "1":
        threading.Thread(target=_aquecer_modelo_local, daemon=True).start()
    return app
