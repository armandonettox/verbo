import { useCallback, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import {
  buscar as buscarNaApi,
  conversar,
  regenerarResposta,
} from '../api/cliente.ts'
import { BuscaContexto } from './buscaContexto.ts'
import type { Conversa, EstadoBusca, Gerando, TurnoChat } from './buscaContexto.ts'

function mensagemDe(e: unknown): string {
  return e instanceof Error ? e.message : 'Nao foi possivel completar a solicitacao.'
}

// Guarda a busca atual acima das rotas, para ela sobreviver a ida e volta
// entre a conversa e a leitura de um capitulo
export function BuscaProvider({ children }: { children: ReactNode }) {
  const [conversa, setConversa] = useState<Conversa | null>(null)
  const [historico, setHistorico] = useState<TurnoChat[]>([])
  const [buscando, setBuscando] = useState(false)
  const [gerando, setGerando] = useState<Gerando>(null)
  const [erro, setErro] = useState<string | null>(null)
  const [erroChat, setErroChat] = useState<string | null>(null)
  // Identifica a conversa atual; "nova busca" ou uma busca nova invalida respostas atrasadas
  const rodada = useRef(0)

  const buscar = useCallback(async (pergunta: string) => {
    const minha = ++rodada.current
    setBuscando(true)
    setErro(null)
    setErroChat(null)
    try {
      const resultado = await buscarNaApi(pergunta)
      if (minha !== rodada.current) return
      setHistorico([])
      setConversa({ pergunta, resultado, resposta: resultado.resposta, quando: new Date() })
    } catch (e) {
      if (minha !== rodada.current) return
      setErro(mensagemDe(e))
    } finally {
      if (minha === rodada.current) setBuscando(false)
    }
  }, [])

  const perguntar = useCallback(
    async (pergunta: string) => {
      if (!conversa || conversa.resposta === null) return false
      const minha = rodada.current
      const anterior = historico
      setErroChat(null)
      setGerando('novo')
      setHistorico([...anterior, { role: 'user', content: pergunta, quando: new Date() }])
      try {
        const { resposta } = await conversar({
          perguntaOriginal: conversa.pergunta,
          respostaOriginal: conversa.resposta,
          versiculos: conversa.resultado.versiculos,
          historico: anterior.map(({ role, content }) => ({ role, content })),
          perguntaNova: pergunta,
        })
        if (minha !== rodada.current) return false
        setHistorico((atual) => [...atual, { role: 'assistant', content: resposta, quando: new Date() }])
        return true
      } catch (e) {
        if (minha !== rodada.current) return false
        // desfaz a pergunta que ficou sem resposta, para o usuario poder tentar de novo
        setHistorico(anterior)
        setErroChat(mensagemDe(e))
        return false
      } finally {
        if (minha === rodada.current) setGerando(null)
      }
    },
    [conversa, historico],
  )

  const regenerarOriginal = useCallback(async () => {
    if (!conversa) return
    const minha = rodada.current
    setErroChat(null)
    setGerando('original')
    try {
      const { resposta } = await regenerarResposta(conversa.pergunta, conversa.resultado.versiculos)
      if (minha !== rodada.current) return
      setConversa((atual) => (atual ? { ...atual, resposta } : atual))
    } catch (e) {
      if (minha !== rodada.current) return
      setErroChat(mensagemDe(e))
    } finally {
      if (minha === rodada.current) setGerando(null)
    }
  }, [conversa])

  const regenerarTurno = useCallback(
    async (indice: number) => {
      if (!conversa || conversa.resposta === null) return
      const pergunta = historico[indice - 1]
      if (!pergunta || pergunta.role !== 'user') return
      const minha = rodada.current
      setErroChat(null)
      setGerando(indice)
      try {
        const { resposta } = await conversar({
          perguntaOriginal: conversa.pergunta,
          respostaOriginal: conversa.resposta,
          versiculos: conversa.resultado.versiculos,
          historico: historico.slice(0, indice - 1).map(({ role, content }) => ({ role, content })),
          perguntaNova: pergunta.content,
        })
        if (minha !== rodada.current) return
        setHistorico((atual) =>
          atual.map((turno, i) => (i === indice ? { ...turno, content: resposta } : turno)),
        )
      } catch (e) {
        if (minha !== rodada.current) return
        setErroChat(mensagemDe(e))
      } finally {
        if (minha === rodada.current) setGerando(null)
      }
    },
    [conversa, historico],
  )

  const novaBusca = useCallback(() => {
    rodada.current++
    setConversa(null)
    setHistorico([])
    setErro(null)
    setErroChat(null)
    setBuscando(false)
    setGerando(null)
  }, [])

  const valor = useMemo<EstadoBusca>(
    () => ({
      conversa,
      historico,
      buscando,
      gerando,
      erro,
      erroChat,
      buscar,
      perguntar,
      regenerarOriginal,
      regenerarTurno,
      novaBusca,
    }),
    [conversa, historico, buscando, gerando, erro, erroChat, buscar, perguntar, regenerarOriginal, regenerarTurno, novaBusca],
  )

  return <BuscaContexto.Provider value={valor}>{children}</BuscaContexto.Provider>
}
