import { useState } from 'react'
import type { FormEvent } from 'react'

interface CampoBuscaProps {
  buscando: boolean
  onBuscar: (pergunta: string) => void
}

function IconeBusca() {
  return (
    <svg
      viewBox="0 0 24 24"
      width="18"
      height="18"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      aria-hidden="true"
    >
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.5-3.5" />
    </svg>
  )
}

function IconeCarregando() {
  return (
    <svg
      className="icone-girando"
      viewBox="0 0 24 24"
      width="18"
      height="18"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      aria-hidden="true"
    >
      <path d="M12 3a9 9 0 1 0 9 9" />
    </svg>
  )
}

export function CampoBusca({ buscando, onBuscar }: CampoBuscaProps) {
  const [pergunta, setPergunta] = useState('')

  function enviar(evento: FormEvent) {
    evento.preventDefault()
    const texto = pergunta.trim()
    if (!texto || buscando) return
    onBuscar(texto)
  }

  return (
    <form className="campo-busca" onSubmit={enviar}>
      <input
        type="text"
        value={pergunta}
        onChange={(e) => setPergunta(e.target.value)}
        placeholder="O que Jesus disse sobre o amor ao proximo?"
        aria-label="Qual e a sua pergunta?"
        maxLength={500}
        autoComplete="off"
      />
      <button type="submit" className="botao-busca" disabled={buscando}>
        {buscando ? <IconeCarregando /> : <IconeBusca />}
        {buscando ? 'Buscando' : 'Buscar'}
      </button>
    </form>
  )
}
