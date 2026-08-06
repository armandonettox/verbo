<p align="center">
  <img src="assets/logo.png" width="150" alt="Verbo">
</p>

# Verbo

RAG fechado sobre a Biblia Catolica, em portugues. Responde perguntas usando so o texto da Biblia como fonte, sem inventar com conhecimento geral do LLM.

App em produção: [overbo.streamlit.app](https://overbo.streamlit.app)

## Origem

O Verbo nasceu na crisma. Comecei a fazer a crisma na igreja catolica junto com a
minha namorada, e ela comentou que sentia falta de uma IA pra aprimorar os
conhecimentos biblicos dela. Aproveitei essa necessidade real pra criar o projeto e
aprender, na pratica, todo o processo de um RAG — com uma regra clara: ele so
responde com base na Biblia que ela escolheu, a mesma usada na crisma.

## Como funciona

1. `data/biblia.json` e agrupado em chunks por capitulo (`scripts/construir_banco.py`) e indexado como embeddings num banco vetorial Chroma.
2. Cada pergunta do usuario e transformada em embedding e comparada por similaridade de cosseno contra esse indice, retornando os versiculos mais relevantes.
3. Os versiculos encontrados (e so eles) sao passados como contexto pro LLM, que sintetiza a resposta citando as referencias usadas.

Embeddings e chat rodam via NVIDIA NIM (`nv-embedqa-e5-v5` e `llama-3.1-8b-instruct`).

## Arquitetura

```
verbo/
├── app.py                  # entrypoint Streamlit (UI + orquestracao de estado)
├── src/verbo/
│   ├── config.py           # variaveis de ambiente e parametros do RAG
│   ├── core/                # clients compartilhados (NVIDIA NIM, Chroma)
│   ├── services/            # logica de negocio pura: busca, resposta, leitura, planos de leitura
│   └── ui/                  # componentes de interface com HTML/JS embutido (audio, copiar, fuso horario)
├── scripts/
│   └── construir_banco.py  # ingestao: le biblia.json e popula o banco vetorial
├── assets/                  # CSS, templates HTML e imagens estaticas
├── data/
│   └── biblia.json         # fonte de dados
└── tests/                   # suite pytest, espelhando services/
```

`services/` concentra regras que nao dependem de Streamlit e sao testadas isoladamente;
`ui/` concentra o que so existe pra renderizar algo na tela. `core/` evita ter o client
da NVIDIA ou do Chroma instanciado em varios lugares diferentes.

## Rodando localmente

```bash
python -m venv .venv
.venv/Scripts/activate        # ou source .venv/bin/activate no Linux/Mac
pip install -r requirements.txt

cp .env.example .secrets/.env  # e preencha NVIDIA_API_KEY

python scripts/construir_banco.py   # so na primeira vez, pra gerar o banco vetorial
streamlit run app.py
```

## Testes

```bash
pip install -r tests/requirements.txt
pytest tests/
```

## Documentacao

Instalacao, configuracao e decisoes de arquitetura tambem estao no meu portfolio:
[armandonetto.com/projetos/verbo](https://armandonetto.com/projetos/verbo/)

## Licenca

Codigo sob [Licenca Verbo 1.0](LICENSE): livre pra ver, estudar,
rodar e modificar sem fins lucrativos. Uso comercial de qualquer forma exige
autorizacao previa por escrito — entre em contato antes de usar o Verbo (ou
derivados) em algo que gere lucro.
