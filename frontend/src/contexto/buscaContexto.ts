import { createContext } from 'react'
import type { ResultadoBusca } from '../api/tipos.ts'

export interface Conversa {
  pergunta: string
  resultado: ResultadoBusca
  // Pode mudar quando o usuario pede para gerar de novo, ou ser nula no modo local
  resposta: string | null
  quando: Date
}

export interface TurnoChat {
  role: 'user' | 'assistant'
  content: string
  quando: Date
}

// Qual resposta esta sendo gerada agora: a original, uma do historico (pelo indice) ou uma nova
export type Gerando = 'original' | 'novo' | number | null

export interface EstadoBusca {
  conversa: Conversa | null
  historico: TurnoChat[]
  buscando: boolean
  gerando: Gerando
  erro: string | null
  erroChat: string | null
  buscar: (pergunta: string) => Promise<void>
  perguntar: (pergunta: string) => Promise<boolean>
  regenerarOriginal: () => Promise<void>
  regenerarTurno: (indice: number) => Promise<void>
  novaBusca: () => void
}

export const BuscaContexto = createContext<EstadoBusca | null>(null)
