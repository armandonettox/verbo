# verbo

## Indice

- [Objetivo](#objetivo)
- [Forma de entrega](#forma-de-entrega)
- [Stack](#stack)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Instalacao](#instalacao)
- [Configuracao](#configuracao)
- [Como usar](#como-usar)
- [Output](#output)
- [Funcionamento](#funcionamento)
- [Adaptacao](#adaptacao)
- [Erros comuns](#erros-comuns)

## Objetivo

RAG fechado sobre a Biblia Catolica Ave Maria, em portugues. Responde perguntas usando so o texto da Biblia como fonte, sem inventar com conhecimento geral do LLM. Projeto publico, pensado para qualquer pessoa usar apos publicacao.

## Forma de entrega

Aplicacao web (Streamlit), hospedada no Streamlit Community Cloud.

## Stack

- Python 3.x
- ChromaDB (banco vetorial local)
- NVIDIA NIM (embeddings + chat completions, free tier)
- Streamlit (interface)
- python-dotenv

## Estrutura do projeto

```
verbo/
    data/
        biblia-ave-maria.json    <- fonte validada (73 livros, 35.450 versiculos)
        construir-banco.py       <- gera embeddings e popula o Chroma
    modules/
        busca.py                 <- consulta o Chroma, retorna versiculos proximos
        resposta.py              <- monta prompt e chama NVIDIA NIM chat completions
    app.py                       <- interface Streamlit
    config.py                    <- configuracoes, nomes de modelo, paths
    .env.example                 <- variaveis necessarias (sem valores reais)
    requirements.txt             <- dependencias
    README.md                    <- este arquivo
```

## Instalacao

### Ambiente virtual

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
```

### Dependencias

```bash
pip install -r requirements.txt
```

## Configuracao

Copie `.env.example` para `.env` e preencha as variaveis:

```
NVIDIA_API_KEY=seu_api_key_aqui
```

Nunca commitar o arquivo `.env` com valores reais.

## Como usar

1. Construir o banco vetorial (executar uma unica vez):

```bash
python data/construir-banco.py
```

2. Iniciar a aplicacao:

```bash
streamlit run app.py
```

## Output

Respostas baseadas exclusivamente nos versiculos da Biblia Ave Maria, com citacao da referencia (livro, capitulo, versiculo).

## Funcionamento

O projeto e composto por 4 pecas:

1. **Banco vetorial (Chroma)** — guarda cada versiculo transformado em vetor, organizado por assunto
2. **Embedding (NVIDIA NIM)** — transforma texto em vetor de significado; calculado uma vez para os versiculos e a cada pergunta nova
3. **Busca por similaridade** — compara a pergunta com os vetores existentes, retorna os N versiculos mais proximos
4. **Geracao da resposta (NVIDIA NIM, chat completions)** — recebe pergunta + versiculos encontrados e responde so com base nisso

## Adaptacao

Para usar com outra fonte de texto:

1. Substituir `biblia-ave-maria.json` pelo arquivo desejado
2. Ajustar o parser em `data/construir-banco.py` conforme a estrutura do novo arquivo
3. Atualizar o prompt em `modules/resposta.py` para refletir a nova fonte

## Erros comuns

| Erro | Causa | Solucao |
|------|-------|---------|
| `FileNotFoundError` | `.env` ausente | Copiar `.env.example` para `.env` |
| `AuthenticationError` | `NVIDIA_API_KEY` invalida | Verificar valor no `.env` |
| `ModuleNotFoundError` | Dependencia faltando | `pip install -r requirements.txt` |
| `FileNotFoundError: biblia-ave-maria.json` | Arquivo nao copiado para `data/` | Copiar o JSON para a pasta `data/` |
