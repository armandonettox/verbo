<p align="center">
  <img src="frontend/public/logo.png" width="150" alt="Verbo">
</p>

# Verbo

[![testes](https://github.com/armandonettox/verbo/actions/workflows/testes.yml/badge.svg)](https://github.com/armandonettox/verbo/actions/workflows/testes.yml)

RAG fechado sobre a Biblia Catolica, em portugues. Responde perguntas usando so o texto da Biblia como fonte, sem inventar com conhecimento geral do LLM.

Alem da busca semantica, o Verbo permite ler qualquer livro e capitulo por
inteiro, ouvir o texto narrado, acompanhar um versiculo do dia e continuar a
conversa com perguntas de acompanhamento sobre a resposta gerada.

Em producao em [verbo.armandonetto.com](https://verbo.armandonetto.com).

## Origem

O Verbo nasceu na crisma. Comecei a fazer a crisma na igreja catolica junto com a
minha namorada, e ela comentou que sentia falta de uma IA pra aprimorar os
conhecimentos biblicos dela. Aproveitei essa necessidade real pra criar o projeto e
aprender, na pratica, todo o processo de um RAG — com uma regra clara: ele so
responde com base na Biblia que ela escolheu, a mesma usada na crisma.

## Como funciona

A pergunta vira um vetor (embedding) e e comparada com os 3602 trechos da Biblia
(um por capitulo, ou parte dele quando o capitulo e longo). Os mais proximos vao
para o LLM, que responde usando so esses versiculos.

Se a API da NVIDIA falhar (limite de uso, fora do ar, modelo aposentado), a busca
cai sozinha para um indice local, gerado com um modelo que roda na propria
maquina. Nesse modo a tela mostra so os versiculos mais proximos, sem resposta
gerada, e avisa que a busca esta simplificada.

## Stack

- **Backend:** Python e FastAPI. A regra de negocio fica em `src/verbo/core/`,
  sem depender do framework web.
- **Busca e resposta:** API da NVIDIA NIM, com `nvidia/nemotron-3-embed-1b` para
  embeddings e `nvidia/nemotron-3-super-120b-a12b` para a resposta. Os nomes dos
  modelos sao variaveis de ambiente, porque a NVIDIA aposenta modelos de tempos em
  tempos.
- **Fallback local:** `intfloat/multilingual-e5-small` via fastembed (ONNX, CPU). Se a NVIDIA
  falhar 2 vezes seguidas, ela e pulada por 60 s (disjuntor) e a busca local responde na hora.
  O modelo local e carregado em segundo plano ao iniciar o backend.
- **Cache:** a primeira resposta de cada pergunta fica num SQLite no volume (so o hash da pergunta e
  a resposta, 14 dias, ate 5000 itens); "gerar novamente" ignora o cache. Livros, capitulos e versiculo
  do dia saem com `Cache-Control`, e as buscas (POST) com `no-store`.
- **Banco vetorial:** ChromaDB, com um indice para cada modelo de embedding.
- **Frontend:** React 19, TypeScript, Vite e React Router, com CSS puro e tema
  claro e escuro.
- **Testes:** pytest, Vitest e Playwright (navegador com tela de computador e de
  celular).
- **Deploy:** containers (Docker e podman-compose) numa VPS, com GitHub Actions.

## Estrutura do projeto

```
backend/
  app/                   # API FastAPI (rotas, esquemas, carga da Biblia)
  Dockerfile
src/verbo/
  config.py
  core/                  # regras de negocio, sem depender de framework web
    busca.py             # busca na NVIDIA com fallback para o indice local
    embedding_local.py   # embeddings locais (multilingual-e5-small)
    resposta.py          # resposta inicial e perguntas de acompanhamento
    erros.py             # mapeia falhas de API para mensagens claras
    leitura.py           # carga dos capitulos, versiculo a versiculo
    versiculo_dia.py     # versiculo do dia, deterministico por data
    ingestao.py          # chunking usado na construcao dos indices
frontend/
  src/                   # telas, componentes e hooks em React
  e2e/                   # testes de ponta a ponta (Playwright)
  Dockerfile             # build do React servido por nginx
scripts/
  construir_banco.py     # gera os indices vetoriais (nvidia e local)
deploy/                  # nginx do host, unit do systemd, script de deploy e guia
tests/
  unit/                  # testam o core, sem rede
  backend/               # testam a API
```

## API

Todas as rotas ficam sob `/api`.

| Rota | O que faz |
|------|-----------|
| `POST /versiculos` | so a busca (com fallback); devolve aviso e versiculos |
| `POST /resposta` | resposta gerada para os versiculos; `usar_cache` so na primeira resposta |
| `POST /buscar` | as duas etapas numa chamada so (nao usada pelo site) |
| `POST /resposta` | gera a resposta de novo a partir dos versiculos |
| `POST /chat` | pergunta de acompanhamento, com o historico |
| `GET /versiculo-do-dia` | versiculo do dia; `data` e a data local do usuario |
| `GET /livros` | livros, com o total de capitulos |
| `GET /capitulos/{livro}/{numero}` | capitulo completo, versiculo a versiculo |
| `GET /saude` | estado da chave, dos dois indices, dos disjuntores e contadores de falha e latencia |

## Rodando localmente

Precisa de Python 3.12 ou mais novo e Node 22 ou mais novo.

```
python -m venv .venv
.venv/Scripts/activate          # ou source .venv/bin/activate no Linux/Mac
pip install -r backend/requirements.txt
cp .env.example .secrets/.env   # preencha NVIDIA_API_KEY
python scripts/construir_banco.py   # gera os indices (a parte local leva uns 15 min)
```

Backend (porta 8010):

```
# Linux/Mac
PYTHONPATH=src:. uvicorn --factory backend.app.main:criar_app --port 8010
# PowerShell
$env:PYTHONPATH="src;."; uvicorn --factory backend.app.main:criar_app --port 8010
```

Frontend, em outro terminal (ele repassa `/api` para o backend na porta 8010):

```
cd frontend
npm install
npm run dev
```

Variaveis opcionais: `VERBO_CHROMA_DB_PATH` (pasta dos indices),
`VERBO_EMBEDDING_MODEL`, `VERBO_CHAT_MODEL` e `VERBO_COLLECTION_NAME` (trocar os
modelos da NVIDIA; ao trocar o embedding, troque tambem a colecao e refaca o indice).
`VERBO_BUSCA_TIMEOUT` (8 s), `VERBO_CHAT_TIMEOUT` (45 s), `VERBO_DISJUNTOR_FALHAS` (2) e
`VERBO_DISJUNTOR_PAUSA` (60 s), `VERBO_CACHE_RESPOSTAS_PATH`, `VERBO_CACHE_TTL_DIAS` (14) e
`VERBO_CACHE_MAX_ITENS` (5000) ajustam os tempos de espera e o disjuntor.

## Testes

```
pip install -r tests/requirements.txt
pytest tests/unit tests/backend      # Python

cd frontend
npm test                             # unidade (Vitest)
npx playwright install chromium      # uma vez
npm run e2e                          # navegador: computador e celular
```

Os testes de ponta a ponta usam a API simulada. Para rodar contra o site no ar
(so leitura): `E2E_URL=https://verbo.armandonetto.com npx playwright test`.

## Deploy

O deploy roda sozinho quando os testes passam na `master`: constroi as imagens,
envia ao GitHub Container Registry e atualiza a VPS, com volta automatica se a
saude falhar. Os detalhes, os passos manuais e a operacao estao em
[deploy/README.md](deploy/README.md).

## Documentacao

Instalacao, configuracao e arquitetura estao no meu portfolio:
[armandonetto.com/projetos/verbo](https://armandonetto.com/projetos/verbo/)

## Licenca

Codigo sob [Licenca Verbo 1.0](LICENSE): livre pra ver, estudar,
rodar e modificar sem fins lucrativos. Uso comercial de qualquer forma exige
autorizacao previa por escrito — entre em contato antes de usar o Verbo (ou
derivados) em algo que gere lucro.
