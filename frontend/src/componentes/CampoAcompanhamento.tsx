import { useState } from 'react'
import type { FormEvent } from 'react'

interface CampoAcompanhamentoProps {
  ocupado: boolean
  onEnviar: (pergunta: string) => Promise<boolean>
}

export function CampoAcompanhamento({ ocupado, onEnviar }: CampoAcompanhamentoProps) {
  const [texto, setTexto] = useState('')

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    const pergunta = texto.trim()
    if (!pergunta || ocupado) return
    // so limpa o campo se deu certo, para o usuario nao perder o que digitou
    if (await onEnviar(pergunta)) setTexto('')
  }

  return (
    <div className="rodape-chat">
      <form className="campo-busca" onSubmit={enviar}>
        <input
          type="text"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Faca uma pergunta de acompanhamento..."
          aria-label="Pergunta de acompanhamento"
          maxLength={500}
          autoComplete="off"
        />
        <button type="submit" className="botao-busca" disabled={ocupado}>
          Enviar
        </button>
      </form>
      <p className="texto-mutado aviso-ia">
        Respostas geradas por IA a partir dos versiculos encontrados. Confira sempre o texto original.
      </p>
    </div>
  )
}
