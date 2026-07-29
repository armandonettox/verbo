# verbo

## Contexto

RAG fechado sobre a Biblia Catolica, em portugues.
Responde perguntas usando so o texto da Biblia como fonte, sem inventar com conhecimento geral do LLM.
Forma de entrega: aplicacao web via Streamlit, hospedada no Streamlit Community Cloud.

## Decisoes ja tomadas (nao reabrir sem motivo)

1. Nome: Verbo (referencia a Joao 1:1, "no principio era o Verbo")
2. Fonte: traducao catolica em portugues (nao referenciada publicamente no repositorio)
3. Arquivo validado: `biblia.json` — 35.450 versiculos, 73 livros, UTF-8 ok
4. Banco vetorial: Chroma (local, gratuito)
5. Embeddings: NVIDIA NIM (free tier)
6. LLM de resposta: NVIDIA NIM (chat completions)
7. Interface: Streamlit
8. Hospedagem: Streamlit Community Cloud
9. Sem GPU local — CPU e suficiente para processar 35k versiculos uma unica vez

## Pendencias (decisoes ainda abertas)

- Qual modelo especifico de embedding da NVIDIA NIM usar
- Qual modelo especifico de chat da NVIDIA NIM usar
- Quantos versiculos retornar por busca (top-k) — definir nos testes
- Estrategia de chunking: versiculo individual ou por capitulo — avaliar nos testes

## Regras

1. **Comentarios no codigo naturais e commits sem atribuicao de IA.**
   Comentarios claros, simples, sem caracteres especiais forcados.
   Commits em portugues, formato `tipo(escopo): descricao`.
   Nunca atribuir autoria a IA.
   **Motivacao:** comentarios decorativos entregam que foram gerados por IA.

2. **Fazer uma pergunta por vez, com sugestao de resposta.**
   Nunca duas ou mais perguntas na mesma mensagem.
   **Motivacao:** TDAH torna multiplas perguntas paralisantes.

3. **Nao despejar informacao de uma vez.**
   Apresentar planos em etapas, confirmar antes de prosseguir.
   **Motivacao:** sobrecarga cognitiva impede absorcao.

4. **Nunca pular para proxima etapa sem autorizacao.**
   Sugerir o proximo passo, aguardar confirmacao explicita.
   **Motivacao:** TDAH precisa de pausas entre etapas para processar.

5. **Sempre ler o arquivo antes de editar.**
   **Motivacao:** editar sem contexto quebra mais do que conserta.

6. **Seguranca de credenciais.**
   Nunca hardcode a `NVIDIA_API_KEY` — sempre via variavel de ambiente ou `.env`.
   `.env` sempre no `.gitignore`. Verificar `.gitignore` antes de qualquer commit.
   **Motivacao:** vazamento de API key e irreversivel e causa custo imediato.

7. **Nao sugerir commits ate o usuario pedir explicitamente.**
   **Motivacao:** o usuario controla o historico do git.

8. **Nomenclatura: hifen como separador.**
   Nomes minusculo, sem acentos. Hifen padrao, underscore so quando linguagem exigir.
   **Motivacao:** padrao unico evita confusao entre projetos.

9. **Manter artefatos do projeto atualizados.**
   - `decisoes.md` no vault: registrar decisoes com data, decisao e motivo
   - `roadmap.canvas`: atualizar ao completar cada passo
   - Este CLAUDE.md e o README.md: manter sincronizados com o estado real
   **Motivacao:** documentos defasados geram erros e retrabalho.

## Memoria do projeto

Use o vault pessoal em `vault-armandonettox/projects/verbo` como memoria.
Contexto, decisoes e aprendizados sao registrados la.
Consultar antes de alteracoes significativas.
