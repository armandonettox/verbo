import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import {
  buscarVersiculos,
  conversar,
  regenerarResposta,
} from '../api/cliente.ts'
import type { ResultadoVersiculos } from '../api/tipos.ts'
import { adicionarAoHistorico } from '../utils/historico.ts'
import { apagarConversa, lerConversa, salvarConversa } from '../utils/persistencia.ts'
import { BuscaContexto } from './buscaContexto.ts'
import type { Conversa, EstadoBusca, Gerando, TurnoChat } from './buscaContexto.ts'

function mensagemDe(e: unknown): string {
  return e instanceof Error ? e.message : 'Nao foi possivel completar a solicitacao.'
}

// Guarda a busca atual acima das rotas, para ela sobreviver a ida e volta
// entre a conversa e a leitura de um capitulo
export function BuscaProvider({ children }: { children: ReactNode }) {
  // Se a pagina foi recarregada, a conversa volta do que ficou guardado na aba
  const [restaurada] = useState(lerConversa)
  const [conversa, setConversa] = useState<Conversa | null>(restaurada?.conversa ?? null)
  const [historico, setHistorico] = useState<TurnoChat[]>(restaurada?.historico ?? [])
  const [buscando, setBuscando] = useState(false)
  const [gerando, setGerando] = useState<Gerando>(null)
  const [erro, setErro] = useState<string | null>(null)
  const [erroChat, setErroChat] = useState<string | null>(null)
  // Identifica a conversa atual; "nova busca" ou uma busca nova invalida respostas atrasadas
  const rodada = useRef(0)
  // Ultima pergunta cuja busca ja foi iniciada: evita buscar de novo quando o endereco
  // /buscar?q=... apenas reflete uma busca que o proprio usuario acabou de fazer
  const ultimaPergunta = useRef<string | null>(restaurada?.conversa.pergunta ?? null)

  useEffect(() => {
    if (conversa) salvarConversa(conversa, historico)
    else apagarConversa()
  }, [conversa, historico])

  const jaIniciou = useCallback((pergunta: string) => ultimaPergunta.current === pergunta, [])

  const buscar = useCallback(async (pergunta: string) => {
    const minha = ++rodada.current
    ultimaPergunta.current = pergunta
    setBuscando(true)
    setErro(null)
    setErroChat(null)
    let resultado: ResultadoVersiculos
    try {
      resultado = await buscarVersiculos(pergunta)
    } catch (e) {
      if (minha === rodada.current) {
        setErro(mensagemDe(e))
        setBuscando(false)
      }
      return
    }
    if (minha !== rodada.current) return

    // os versiculos aparecem na hora; a resposta chega logo depois
    adicionarAoHistorico(pergunta)
    setHistorico([])
    setConversa({ pergunta, resultado, resposta: null, citacoes: [], quando: new Date() })
    setBuscando(false)
    // no modo local nao ha resposta, e sem versiculos nao ha o que responder
    if (resultado.modo !== 'nvidia' || resultado.versiculos.length === 0) return

    setGerando('original')
    try {
      const { resposta, citacoes_nao_confirmadas } = await regenerarResposta(pergunta, resultado.versiculos, true)
      if (minha !== rodada.current) return
      setConversa((atual) =>
        atual ? { ...atual, resposta, citacoes: citacoes_nao_confirmadas ?? [] } : atual,
      )
    } catch (e) {
      if (minha !== rodada.current) return
      // os versiculos continuam na tela e o botao "Gerar resposta" permite tentar de novo
      setErroChat(mensagemDe(e))
    } finally {
      if (minha === rodada.current) setGerando(null)
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
        const { resposta, citacoes_nao_confirmadas } = await conversar({
          perguntaOriginal: conversa.pergunta,
          respostaOriginal: conversa.resposta,
          versiculos: conversa.resultado.versiculos,
          historico: anterior.map(({ role, content }) => ({ role, content })),
          perguntaNova: pergunta,
        })
        if (minha !== rodada.current) return false
        setHistorico((atual) => [
          ...atual,
          { role: 'assistant', content: resposta, citacoes: citacoes_nao_confirmadas ?? [], quando: new Date() },
        ])
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
      const { resposta, citacoes_nao_confirmadas } = await regenerarResposta(
        conversa.pergunta,
        conversa.resultado.versiculos,
        // se a primeira resposta falhou, esta ainda e a primeira: pode usar o cache
        conversa.resposta === null,
      )
      if (minha !== rodada.current) return
      setConversa((atual) =>
        atual ? { ...atual, resposta, citacoes: citacoes_nao_confirmadas ?? [] } : atual,
      )
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
        const { resposta, citacoes_nao_confirmadas } = await conversar({
          perguntaOriginal: conversa.pergunta,
          respostaOriginal: conversa.resposta,
          versiculos: conversa.resultado.versiculos,
          historico: historico.slice(0, indice - 1).map(({ role, content }) => ({ role, content })),
          perguntaNova: pergunta.content,
        })
        if (minha !== rodada.current) return
        setHistorico((atual) =>
          atual.map((turno, i) =>
            i === indice ? { ...turno, content: resposta, citacoes: citacoes_nao_confirmadas ?? [] } : turno,
          ),
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
    ultimaPergunta.current = null
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
      jaIniciou,
    }),
    [
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
      jaIniciou,
    ],
  )

  return <BuscaContexto.Provider value={valor}>{children}</BuscaContexto.Provider>
}
