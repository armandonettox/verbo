<p align="center">
  <img src="assets/logo.png" width="150" alt="Verbo">
</p>

# Verbo

RAG fechado sobre a Biblia Catolica Ave Maria, em portugues. Responde perguntas usando so o texto da Biblia como fonte, sem inventar com conhecimento geral do LLM.

## Stack

- Python
- ChromaDB (banco vetorial local)
- NVIDIA NIM (embeddings + chat completions, free tier)
- Streamlit (interface)

## Estrutura

```
verbo/
    data/
        biblia-ave-maria.json    fonte (73 livros, 35.450 versiculos)
        construir-banco.py       gera embeddings e popula o Chroma
    modules/
        busca.py                 consulta o Chroma, retorna versiculos proximos
        resposta.py              monta prompt e chama NVIDIA NIM chat completions
    assets/                      logo e favicon
    app.py                       interface Streamlit
    config.py                    configuracoes, nomes de modelo, paths
    teste-conexao.py             script de diagnostico da API NVIDIA NIM
```

## Como rodar localmente

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha a `NVIDIA_API_KEY` (gratis em https://build.nvidia.com).

Construa o banco vetorial uma unica vez:

```bash
python data/construir-banco.py
```

Rode o app:

```bash
streamlit run app.py
```

## Limitacoes conhecidas

A busca por similaridade (top-k=8) funciona bem para perguntas diretas ("quem foi X", "o que aconteceu em Y"), mas pode nao encontrar o versiculo mais classico para perguntas conceituais amplas (ex.: "o que Jesus disse sobre o amor ao proximo" nem sempre traz Marcos 12:31). Melhorar isso passa por trocar o modelo de embedding ou mudar a estrategia de chunking (por capitulo em vez de versiculo isolado) — ainda nao feito.
