<p align="center">
  <img src="assets/logo.png" width="150" alt="Verbo">
</p>

# Verbo

RAG fechado sobre a Biblia Catolica, em portugues. Responde perguntas usando so o texto da Biblia como fonte, sem inventar com conhecimento geral do LLM.

Alem da busca semantica, o Verbo permite ler qualquer livro e capitulo por
inteiro, ouvir o texto narrado, acompanhar um versiculo do dia e continuar a
conversa com perguntas de acompanhamento sobre a resposta gerada.

Em producao em [overbo.streamlit.app](https://overbo.streamlit.app).

## Origem

O Verbo nasceu na crisma. Comecei a fazer a crisma na igreja catolica junto com a
minha namorada, e ela comentou que sentia falta de uma IA pra aprimorar os
conhecimentos biblicos dela. Aproveitei essa necessidade real pra criar o projeto e
aprender, na pratica, todo o processo de um RAG — com uma regra clara: ele so
responde com base na Biblia que ela escolheu, a mesma usada na crisma.

## Stack

Python, Streamlit, ChromaDB (banco vetorial local) e a API da NVIDIA NIM para
embeddings (`nv-embedqa-e5-v5`) e geracao de resposta (`llama-3.1-8b-instruct`).

## Estrutura do projeto

```
app.py                  # entrypoint do Streamlit (fino, so chama a UI)
src/verbo/
  config.py
  core/                  # regras de negocio, sem depender de streamlit
    busca.py             # embeddings + busca semantica no ChromaDB
    resposta.py          # chamadas ao LLM (resposta inicial e continuacao)
    erros.py             # mapeia falhas da API pra mensagens claras ao usuario
    leitura.py           # parsing dos capitulos e texto pra narracao
    plano_livre.py        # agrupamento de capitulos por livro
    versiculo_dia.py      # versiculo do dia, deterministico por data
    ingestao.py           # chunking usado na construcao do banco vetorial
    util.py                # helpers puros (busca de capitulo, resumo de texto)
  ui/                     # tudo que depende do streamlit
    pagina.py             # composicao da pagina principal
    cache.py              # cache dos dados carregados do disco
    plano_livre.py, audio_widget.py, acoes_chat.py, fuso_horario.py
scripts/
  construir_banco.py     # roda uma unica vez pra popular o ChromaDB
tests/
  unit/                  # testam so o core, sem rede nem streamlit
  integration/           # chamada real a API, roda manualmente
```

A separacao core/ui existe pra deixar a logica de negocio (busca, geracao de
resposta, regras do versiculo do dia) testavel sem precisar simular o
Streamlit ou fazer chamada de rede. Cache e componentes visuais ficam isolados
na camada ui.

## Rodando localmente

```
python -m venv .venv
.venv/Scripts/activate          # ou source .venv/bin/activate no Linux/Mac
pip install -r requirements.txt
cp .env.example .secrets/.env   # preencha NVIDIA_API_KEY
python scripts/construir_banco.py   # popula o banco vetorial (uma vez)
streamlit run app.py
```

## Testes

```
pip install -r tests/requirements.txt
pytest tests/unit
```

## Documentacao

Instalacao, configuracao e arquitetura estao no meu portfolio:
[armandonetto.com/projetos/verbo](https://armandonetto.com/projetos/verbo/)

## Licenca

Codigo sob [Licenca Verbo 1.0](LICENSE): livre pra ver, estudar,
rodar e modificar sem fins lucrativos. Uso comercial de qualquer forma exige
autorizacao previa por escrito — entre em contato antes de usar o Verbo (ou
derivados) em algo que gere lucro.
