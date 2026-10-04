import { useCallback, useEffect, useState } from 'react'

const CHAVE = 'barra-lateral'
// Mesmo ponto de corte do CSS (index.css): abaixo disso a barra vira uma gaveta
const TELA_ESTREITA = '(max-width: 800px)'

function telaEstreita(): boolean {
  return typeof window.matchMedia === 'function' && window.matchMedia(TELA_ESTREITA).matches
}

function barraSalvaAberta(): boolean {
  try {
    return localStorage.getItem(CHAVE) !== 'fechada'
  } catch {
    // localStorage pode estar bloqueado (aba privada, cookies desativados)
    return true
  }
}

function salvar(aberta: boolean) {
  try {
    localStorage.setItem(CHAVE, aberta ? 'aberta' : 'fechada')
  } catch {
    // sem persistencia, a escolha vale so ate fechar a aba
  }
}

// Barra lateral que abre e fecha. No computador lembra a escolha; no celular e uma gaveta que
// comeca fechada e fecha ao tocar fora, com Esc ou ao trocar de tela.
export function useBarraLateral() {
  const [estreita, setEstreita] = useState(telaEstreita)
  const [aberta, setAberta] = useState(() => (telaEstreita() ? false : barraSalvaAberta()))

  useEffect(() => {
    if (typeof window.matchMedia !== 'function') return
    const consulta = window.matchMedia(TELA_ESTREITA)
    const aoMudar = () => {
      setEstreita(consulta.matches)
      // virou celular: fecha a gaveta; voltou ao computador: restaura a escolha salva
      setAberta(consulta.matches ? false : barraSalvaAberta())
    }
    consulta.addEventListener('change', aoMudar)
    return () => consulta.removeEventListener('change', aoMudar)
  }, [])

  const alternar = useCallback(() => {
    setAberta((atual) => {
      const nova = !atual
      if (!telaEstreita()) salvar(nova)
      return nova
    })
  }, [])

  const fechar = useCallback(() => setAberta(false), [])

  useEffect(() => {
    if (!estreita || !aberta) return
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === 'Escape') setAberta(false)
    }
    document.addEventListener('keydown', aoTeclar)
    return () => document.removeEventListener('keydown', aoTeclar)
  }, [estreita, aberta])

  return { aberta, estreita, alternar, fechar }
}
