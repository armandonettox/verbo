import type {
  Capitulo,
  Livro,
  ResultadoVersiculos,
  Saude,
  Turno,
  Versiculo,
  VersiculoDia,
} from './tipos.ts'

const MENSAGEM_PADRAO = 'Nao foi possivel completar a solicitacao. Tente novamente.'

// Erro com a mensagem em portugues que a API devolve em `detail`
export class ErroApi extends Error {
  status: number

  constructor(mensagem: string, status: number) {
    super(mensagem)
    this.name = 'ErroApi'
    this.status = status
  }
}

async function chamar<T>(caminho: string, opcoes?: RequestInit): Promise<T> {
  let resposta: Response
  try {
    resposta = await fetch(caminho, opcoes)
  } catch {
    throw new ErroApi('Nao foi possivel conectar ao servidor. Verifique sua internet e tente novamente.', 0)
  }

  if (!resposta.ok) {
    let mensagem = MENSAGEM_PADRAO
    try {
      const corpo = await resposta.json()
      // 422 traz uma lista de erros de validacao; so 503 e 404 trazem texto pronto
      if (typeof corpo.detail === 'string') mensagem = corpo.detail
    } catch {
      // corpo sem JSON: mantem a mensagem padrao
    }
    throw new ErroApi(mensagem, resposta.status)
  }
  return resposta.json() as Promise<T>
}

function enviar<T>(caminho: string, corpo: unknown): Promise<T> {
  return chamar<T>(caminho, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(corpo),
  })
}

// O servidor roda em UTC, entao a data do "hoje" vem do navegador
export function dataLocalISO(agora: Date = new Date()): string {
  const mes = String(agora.getMonth() + 1).padStart(2, '0')
  const dia = String(agora.getDate()).padStart(2, '0')
  return `${agora.getFullYear()}-${mes}-${dia}`
}

export function buscarVersiculos(pergunta: string): Promise<ResultadoVersiculos> {
  return enviar('/api/versiculos', { pergunta })
}

// usarCache: na primeira resposta de uma busca o servidor pode devolver a que ja tinha guardada;
// "gerar novamente" passa false para sempre pedir uma resposta nova
export function regenerarResposta(
  pergunta: string,
  versiculos: Versiculo[],
  usarCache = false,
): Promise<{ resposta: string }> {
  return enviar('/api/resposta', { pergunta, versiculos, usar_cache: usarCache })
}

export function conversar(dados: {
  perguntaOriginal: string
  respostaOriginal: string
  versiculos: Versiculo[]
  historico: Turno[]
  perguntaNova: string
}): Promise<{ resposta: string }> {
  return enviar('/api/chat', {
    pergunta_original: dados.perguntaOriginal,
    resposta_original: dados.respostaOriginal,
    versiculos: dados.versiculos,
    historico: dados.historico,
    pergunta_nova: dados.perguntaNova,
  })
}

export function versiculoDoDia(data: string = dataLocalISO()): Promise<VersiculoDia> {
  return chamar(`/api/versiculo-do-dia?data=${encodeURIComponent(data)}`)
}

// A lista de livros nao muda, entao a tela de leitura e o seletor dividem uma
// unica chamada. Se der erro, o cache e descartado para tentar de novo depois.
let livrosEmCache: Promise<Livro[]> | null = null

export function listarLivros(): Promise<Livro[]> {
  if (!livrosEmCache) {
    livrosEmCache = chamar<Livro[]>('/api/livros').catch((erro) => {
      livrosEmCache = null
      throw erro
    })
  }
  return livrosEmCache
}

export function limparCacheLivros() {
  livrosEmCache = null
}

export function obterCapitulo(livro: string, numero: number): Promise<Capitulo> {
  return chamar(`/api/capitulos/${encodeURIComponent(livro)}/${numero}`)
}

export function saude(): Promise<Saude> {
  return chamar('/api/saude')
}
