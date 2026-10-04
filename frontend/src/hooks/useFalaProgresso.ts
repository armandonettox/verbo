import { useCallback, useEffect, useRef, useState } from 'react'

const VELOCIDADE = 0.95
const PALAVRAS_POR_MINUTO = 155 * VELOCIDADE
const PASSO_MS = 200

export type EstadoFala = 'parado' | 'falando' | 'pausado'

export function formatarTempo(segundos: number): string {
  const total = Math.max(0, Math.round(segundos))
  const minutos = Math.floor(total / 60)
  const resto = total % 60
  return `${minutos}:${resto < 10 ? '0' : ''}${resto}`
}

// Leitura de um texto longo com pausa e tempo estimado. O navegador nao informa o
// progresso real da fala, entao o tempo e uma estimativa pelo numero de palavras.
// Quem usa deve trocar a `key` do componente quando o texto mudar.
export function useFalaProgresso(texto: string) {
  const suportado = typeof window !== 'undefined' && 'speechSynthesis' in window
  const [estado, setEstado] = useState<EstadoFala>('parado')
  const [decorrido, setDecorrido] = useState(0)
  const temporizador = useRef<number | undefined>(undefined)
  const iniciou = useRef(false)

  const palavras = Math.max(texto.split(/\s+/).filter(Boolean).length, 1)
  const total = Math.round((palavras / PALAVRAS_POR_MINUTO) * 60)

  const pararTemporizador = useCallback(() => {
    window.clearInterval(temporizador.current)
    temporizador.current = undefined
  }, [])

  const iniciarTemporizador = useCallback(() => {
    pararTemporizador()
    temporizador.current = window.setInterval(
      () => setDecorrido((s) => s + PASSO_MS / 1000),
      PASSO_MS,
    )
  }, [pararTemporizador])

  const resetar = useCallback(() => {
    pararTemporizador()
    iniciou.current = false
    setDecorrido(0)
    setEstado('parado')
  }, [pararTemporizador])

  const alternar = useCallback(() => {
    if (!suportado) return
    const sintese = window.speechSynthesis

    if (estado === 'falando') {
      sintese.pause()
      pararTemporizador()
      setEstado('pausado')
      return
    }
    if (estado === 'pausado') {
      sintese.resume()
      iniciarTemporizador()
      setEstado('falando')
      return
    }

    sintese.cancel()
    const fala = new SpeechSynthesisUtterance(texto)
    fala.lang = 'pt-BR'
    fala.rate = VELOCIDADE
    fala.onend = resetar
    fala.onerror = resetar
    iniciou.current = true
    setDecorrido(0)
    setEstado('falando')
    iniciarTemporizador()
    sintese.speak(fala)
  }, [suportado, estado, texto, pararTemporizador, iniciarTemporizador, resetar])

  useEffect(
    () => () => {
      window.clearInterval(temporizador.current)
      // so cancela se foi este leitor que comecou a falar
      if (iniciou.current) window.speechSynthesis.cancel()
    },
    [],
  )

  return { suportado, estado, decorrido, total, alternar }
}
