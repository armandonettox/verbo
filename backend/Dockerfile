# Build a partir da raiz do repo: docker build -f backend/Dockerfile .
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src:/app \
    VERBO_BIBLE_JSON_PATH=/app/data/biblia.json \
    VERBO_CHROMA_DB_PATH=/dados/chroma-db \
    VERBO_MODELO_CACHE_DIR=/dados/modelos \
    HF_HOME=/dados/modelos \
    VERBO_AQUECER_MODELO_LOCAL=1

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY src/ src/
COPY backend/ backend/
COPY scripts/ scripts/
COPY data/biblia.json data/biblia.json

# /dados guarda os indices vetoriais e o modelo local (volume na VPS)
RUN useradd --create-home --uid 1000 verbo \
    && mkdir -p /dados \
    && chown -R verbo:verbo /dados /app
USER verbo

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/saude', timeout=4).status == 200 else 1)"

CMD ["uvicorn", "--factory", "backend.app.main:criar_app", "--host", "0.0.0.0", "--port", "8000"]
