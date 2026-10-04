import { useCallback, useEffect, useRef, useState } from 'react'

const VELOCIDADE = 0.95

// Leitura em voz alta com a voz do proprio navegador (Web Speech API)
export function useFala() {
  const suportado = typeof window !== 'undefined' && 'speechSynthesis' in window
  const [falando, setFalando] = useState(false)
  // So cancela ao desmontar se foi este componente que comecou a falar
  const iniciouFala = useRef(false)

  const parar = useCallback(() => {
    if (!suportado) return
    window.speechSynthesis.cancel()
    iniciouFala.current = false
    setFalando(false)
  }, [suportado])

  const falar = useCallback(
    (texto: string) => {
      if (!suportado) return
      // Garante que uma fala anterior de outro botao nao fique sobreposta
      window.speechSynthesis.cancel()
      const fala = new SpeechSynthesisUtterance(texto)
      fala.lang = 'pt-BR'
      fala.rate = VELOCIDADE
      fala.onend = () => {
        iniciouFala.current = false
        setFalando(false)
      }
      fala.onerror = fala.onend
      iniciouFala.current = true
      setFalando(true)
      window.speechSynthesis.speak(fala)
    },
    [suportado],
  )

  useEffect(
    () => () => {
      if (iniciouFala.current) window.speechSynthesis.cancel()
    },
    [],
  )

  return { suportado, falando, falar, parar }
}
