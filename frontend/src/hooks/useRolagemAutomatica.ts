import { useCallback, useEffect, useRef, useState } from 'react'
import type { RefObject } from 'react'

// Mesma cadencia do app antigo: 1 px a cada 40 ms (cerca de 25 px por segundo)
const PASSO_MS = 40
const TECLAS_DE_ROLAGEM = new Set(['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', ' '])

function elementoDeRolagem(): Element {
  return document.scrollingElement ?? document.documentElement
}

function paginaRolavel(): boolean {
  const el = elementoDeRolagem()
  return el.scrollHeight > el.clientHeight + 4
}

// "Modo leitura": a pagina desce sozinha, devagar, para ler sem tocar na tela. Para sozinha no
// fim, quando a pagina deixa de ser rolavel, e assim que a pessoa assume o controle (roda do
// mouse, toque ou teclas de rolagem). `ignorar` e o botao que liga e desliga: um toque nele
// nao pode contar como "assumir o controle", senao desligar religaria.
export function useRolagemAutomatica(ignorar: RefObject<HTMLElement | null>) {
  const [rolando, setRolando] = useState(false)
  const [rolavel, setRolavel] = useState(paginaRolavel)
  const intervalo = useRef<number | undefined>(undefined)

  const parar = useCallback(() => {
    window.clearInterval(intervalo.current)
    intervalo.current = undefined
    setRolando(false)
  }, [])

  // So faz sentido oferecer o modo quando ha o que rolar. Chamada por eventos (tamanho da tela e
  // do conteudo mudando), nunca direto dentro de um efeito.
  const medir = useCallback(() => {
    const ok = paginaRolavel()
    setRolavel(ok)
    if (!ok) parar()
  }, [parar])

  useEffect(() => {
    window.addEventListener('resize', medir)
    let observador: ResizeObserver | undefined
    if (typeof ResizeObserver !== 'undefined') {
      // o observador avisa na primeira observacao e a cada mudanca de tamanho do conteudo
      observador = new ResizeObserver(medir)
      observador.observe(document.body)
    }
    return () => {
      window.removeEventListener('resize', medir)
      observador?.disconnect()
    }
  }, [medir])

  const alternar = useCallback(() => {
    if (intervalo.current !== undefined) {
      parar()
      return
    }
    setRolando(true)
    intervalo.current = window.setInterval(() => {
      const el = elementoDeRolagem()
      window.scrollBy(0, 1)
      if (el.scrollTop + el.clientHeight >= el.scrollHeight - 2) parar()
    }, PASSO_MS)
  }, [parar])

  useEffect(() => {
    if (!rolando) return
    // o alvo pode ser a propria janela (nao e um no): so conta como "no botao" se for um elemento dele
    const dentroDoBotao = (evento: Event) =>
      evento.target instanceof Node && (ignorar.current?.contains(evento.target) ?? false)
    const aoAssumir = (evento: Event) => {
      if (!dentroDoBotao(evento)) parar()
    }
    const aoTeclar = (evento: KeyboardEvent) => {
      if (TECLAS_DE_ROLAGEM.has(evento.key) && !dentroDoBotao(evento)) parar()
    }
    window.addEventListener('wheel', aoAssumir, { passive: true })
    window.addEventListener('touchstart', aoAssumir, { passive: true })
    window.addEventListener('keydown', aoTeclar)
    return () => {
      window.removeEventListener('wheel', aoAssumir)
      window.removeEventListener('touchstart', aoAssumir)
      window.removeEventListener('keydown', aoTeclar)
    }
  }, [rolando, parar, ignorar])

  // ao sair da tela (ex: trocar de capitulo) nada pode continuar rolando
  useEffect(() => () => window.clearInterval(intervalo.current), [])

  return { rolando, rolavel, alternar }
}
