// Formatos devolvidos pela API (ver backend/app/schemas.py)

export type ModoBusca = 'nvidia' | 'local'

export interface Versiculo {
  referencia: string
  texto: string
  similaridade: number | null
  livro: string | null
  capitulo: number | null
}

export interface ResultadoBusca {
  pergunta: string
  modo: ModoBusca
  resposta: string | null
  aviso: string | null
  versiculos: Versiculo[]
}

export interface Turno {
  role: 'user' | 'assistant'
  content: string
}

export interface VersiculoDia {
  referencia: string
  texto: string
  data: string
}

export interface Livro {
  livro: string
  indice_inicial: number
  total_capitulos: number
}

export interface VersiculoCapitulo {
  versiculo: number
  texto: string
}

export interface Capitulo {
  livro: string
  capitulo: number
  total_capitulos_livro: number
  versiculos: VersiculoCapitulo[]
}

export interface Saude {
  status: 'ok' | 'degradado'
  nvidia_configurada: boolean
  indice_nvidia: boolean
  indice_local: boolean
}
