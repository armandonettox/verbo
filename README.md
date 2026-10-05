<p align="center">
  <img src="frontend/public/logo.png" width="150" alt="Verbo">
</p>

# Verbo

[![testes](https://github.com/armandonettox/verbo/actions/workflows/testes.yml/badge.svg)](https://github.com/armandonettox/verbo/actions/workflows/testes.yml)

RAG fechado sobre a Biblia Catolica, em portugues. Responde perguntas usando so o texto da Biblia como fonte, sem inventar com conhecimento geral do LLM.

Em producao em [verbo.armandonetto.com](https://verbo.armandonetto.com).

## O que o Verbo faz

- **Busca semantica:** a pergunta encontra os versiculos mais proximos pelo sentido, nao so pelas
  palavras. Os versiculos aparecem em cerca de 1 segundo e a resposta chega logo depois.
- **Resposta so com a Biblia:** o LLM recebe apenas os versiculos encontrados. Se a resposta citar
  uma passagem que nao estava entre eles, a tela avisa e linka o capitulo para conferir.
- **Conversa:** perguntas de acompanhamento sobre a resposta, com opcao de gerar de novo, copiar e ouvir
  a resposta narrada.
- **Continua funcionando sem IA:** se a API da NVIDIA falhar, a busca cai sozinha para um indice local
  e mostra so os versiculos, com aviso.
- **Leitura:** qualquer livro e capitulo por inteiro, com navegacao entre capitulos, modo de rolagem
  automatica, audio e versiculo do dia.
- **Link da busca:** cada busca tem um endereco (`/buscar?q=...`) que pode ser copiado e aberto depois.
  A conversa sobrevive a recarregar a pagina e as ultimas 10 buscas ficam a mao, guardadas so no
  navegador e apagaveis.
- **Celular e acessibilidade:** a barra lateral vira gaveta em tela estreita ou baixa, tema claro e
  escuro, e as telas passam em varredura de acessibilidade automatica (WCAG AA).

## Origem

O Verbo nasceu na crisma. Comecei a fazer a crisma na igreja catolica junto com a
minha namorada, e ela comentou que sentia falta de uma IA pra aprimorar os
conhecimentos biblicos dela. Aproveitei essa necessidade real pra criar o projeto e
aprender, na pratica, todo o processo de um RAG — com uma regra clara: ele so
responde com base na Biblia que ela escolheu, a mesma usada na crisma.

## Como funciona

1. **Indexacao (uma vez):** a Biblia e dividida em 3602 trechos (um por capitulo, ou parte dele quando o
   capitulo e longo, sem quebrar versiculo). Cada trecho vira um vetor (embedding) guardado no ChromaDB.
2. **Versiculos:** a pergunta vira um vetor e e comparada com os trechos. Os mais proximos acima de um
   corte de similaridade seguem para o proximo passo. Perguntas sem relacao com a Biblia ficam sem
   resultado.
3. **Resposta:** o LLM responde usando exclusivamente esses versiculos. Depois, o backend le os
   capitulos citados e compara com os que foram enviados (`citacoes_nao_confirmadas`).
4. **Cache:** a primeira resposta de cada pergunta fica guardada (so o hash e a resposta, sem texto de
   usuario), entao a mesma pergunta responde em fracao de segundo. "Gerar novamente" ignora o cache.

### Quando a IA falha

- A busca na NVIDIA tem timeout de 8 s e o chat de 45 s, sem tentar de novo.
- Depois de 2 falhas seguidas o servico e pulado por 60 s (disjuntor): a busca local responde na hora e o
  usuario nao espera o timeout a cada pergunta. Passada a pausa, uma tentativa de teste decide se volta.
- O fallback usa `intfloat/multilingual-e5-small` rodando na propria maquina e devolve os 30 versiculos
  mais proximos, sem resposta gerada. O modelo e carregado em segundo plano ao iniciar o backend.
- Se so a resposta falhar, os versiculos continuam na tela e ha um botao para gerar de novo.
- `GET /api/saude` mostra o estado dos disjuntores e contadores de falha e latencia (em memoria, sem dados
  de usuario).

### Qualidade medida

Com 30 perguntas validadas (`tests/avaliacao/`), o capitulo esperado aparece entre os 10 primeiros em
84,6% dos casos no indice da NVIDIA, e as perguntas sem relacao com a Biblia ficam sem resultado. Nas
respostas geradas, 168 citacoes conferidas e nenhuma fora dos versiculos enviados. O ponto fraco sao as
perguntas muito abstratas (por exemplo "por que Deus permite o sofrimento?"). Hibrido BM25, trechos
menores e reescrita da pergunta foram testados e nao entraram porque nao melhoraram o conjunto.

## Stack

- **Backend:** Python e FastAPI. A regra de negocio fica em `src/verbo/core/`, sem depender do framework web.
- **Busca e resposta:** API da NVIDIA NIM, com `nvidia/nemotron-3-embed-1b` para embeddings e
  `nvidia/nemotron-3-super-120b-a12b` para a resposta. Os nomes dos modelos sao variaveis de ambiente,
  porque a NVIDIA aposenta modelos de tempos em tempos.
- **Fallback local:** `intfloat/multilingual-e5-small` via fastembed (ONNX, CPU).
- **Banco vetorial:** ChromaDB, com um indice para cada modelo de embedding.
- **Cache:** SQLite no volume do container.
- **Frontend:** React 19, TypeScript, Vite e React Router, com CSS puro e tema claro e escuro.
- **Testes:** pytest, Vitest, Playwright (computador e celular) e axe-core (acessibilidade).
- **Deploy:** containers (Docker e podman-compose) numa VPS, nginx e Cloudflare na frente, GitHub Actions.

## Estrutura do projeto

```
backend/
  app/                   # API FastAPI (rotas, esquemas, carga da Biblia)
  Dockerfile
src/verbo/
  config.py              # configuracao por variavel de ambiente
  core/                  # regras de negocio, sem depender de framework web
    busca.py             # busca na NVIDIA com fallback para o indice local
    disjuntor.py         # pula um servico que esta falhando por um tempo
    metricas.py          # contadores e latencias em memoria
    embedding_local.py   # embeddings locais (multilingual-e5-small)
    resposta.py          # resposta inicial e perguntas de acompanhamento
    cache_respostas.py   # cache das respostas em SQLite
    citacoes.py          # confere as passagens citadas contra os versiculos enviados
    erros.py             # mapeia falhas de API para mensagens claras
    leitura.py           # carga dos capitulos, versiculo a versiculo
    versiculo_dia.py     # versiculo do dia, deterministico por data
    ingestao.py          # chunking usado na construcao dos indices
    avaliacao.py         # metricas da avaliacao da busca
frontend/
  src/                   # paginas, componentes, hooks e utilitarios em React
  e2e/                   # ponta a ponta: barra lateral, leitura, link da busca,
                         # acessibilidade e teclado virtual (Playwright)
  Dockerfile             # build do React servido por nginx
scripts/
  construir_banco.py     # gera os indices vetoriais (nvidia e local)
  avaliar_busca.py       # mede a qualidade da busca
deploy/                  # nginx do host, unit do systemd, script de deploy e guia
tests/
  unit/                  # testam o core, sem rede
  backend/               # testam a API
  avaliacao/             # perguntas validadas e linha de base da busca
```

## API

Todas as rotas ficam sob `/api`.

| Rota | O que faz |
|------|-----------|
| `POST /versiculos` | busca (com fallback); devolve modo, aviso e versiculos |
| `POST /resposta` | gera a resposta para os versiculos; `usar_cache` so na primeira resposta de uma busca; devolve `citacoes_nao_confirmadas` |
| `POST /chat` | pergunta de acompanhamento, com o historico |
| `POST /buscar` | versiculos e resposta numa chamada so (apoio; o site usa as duas rotas acima) |
| `GET /versiculo-do-dia` | versiculo do dia; `data` e a data local do usuario |
| `GET /livros` | livros, com o total de capitulos |
| `GET /capitulos/{livro}/{numero}` | capitulo completo, versiculo a versiculo |
| `GET /saude` | chave, indices, disjuntores, contadores e latencias |

Livros e capitulos saem com `Cache-Control` de um dia; as rotas `POST` saem com `no-store`.

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

### Variaveis de ambiente

Todas sao opcionais, exceto `NVIDIA_API_KEY`.

| Variavel | Padrao | Para que serve |
|----------|--------|----------------|
| `NVIDIA_API_KEY` | | chave da API da NVIDIA |
| `VERBO_CHROMA_DB_PATH` | `chroma-db` | pasta dos indices |
| `VERBO_EMBEDDING_MODEL`, `VERBO_CHAT_MODEL` | modelos nemotron | modelos da NVIDIA |
| `VERBO_COLLECTION_NAME`, `VERBO_COLLECTION_NAME_LOCAL` | `biblia-nemotron`, `biblia-local` | colecoes dos indices (ao trocar o embedding, troque a colecao e refaca o indice) |
| `VERBO_BUSCA_TIMEOUT`, `VERBO_CHAT_TIMEOUT` | `8`, `45` | segundos de espera pela NVIDIA |
| `VERBO_DISJUNTOR_FALHAS`, `VERBO_DISJUNTOR_PAUSA` | `2`, `60` | falhas seguidas para abrir e segundos de pausa |
| `VERBO_TOP_K_LOCAL` | `30` | versiculos devolvidos pelo fallback local |
| `VERBO_CACHE_RESPOSTAS_PATH` | desligado | arquivo SQLite do cache de respostas |
| `VERBO_CACHE_TTL_DIAS`, `VERBO_CACHE_MAX_ITENS` | `14`, `5000` | validade e tamanho do cache |

## Testes

```
pip install -r tests/requirements.txt
pytest tests/unit tests/backend      # Python

cd frontend
npm test                             # unidade (Vitest)
npx playwright install chromium      # uma vez
npm run e2e                          # navegador: computador e celular, acessibilidade e teclado virtual
```

Os testes de ponta a ponta usam a API simulada. Para rodar contra o site no ar
(so leitura): `E2E_URL=https://verbo.armandonetto.com npx playwright test`.

### Qualidade da busca

`tests/avaliacao/perguntas.json` tem 30 perguntas com os capitulos esperados. O script mede
quantas vezes o capitulo certo aparece entre os primeiros resultados (acerto em 5, 10 e 40, e MRR) e se
as perguntas sem relacao com a Biblia ficam sem resultado. Usa os indices reais, entao nao roda no CI:

```
python scripts/avaliar_busca.py --indice ambos --comparar tests/avaliacao/linha-de-base.json
python scripts/avaliar_busca.py --indice nvidia --respostas   # gera respostas reais e mede as citacoes fora dos versiculos
```

Para testar outro jeito de indexar sem mexer nos indices em uso, crie colecoes ao lado
(`scripts/construir_banco.py --tamanho-trecho 600 --com-referencia --sufixo=-t600r`) e avalie com
`--sufixo=-t600r --total-lido 80`.

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
