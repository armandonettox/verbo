import { useRef } from 'react'
import { useRolagemAutomatica } from '../hooks/useRolagemAutomatica.ts'

// Botao flutuante "Rolar" / "Parar" do modo leitura (rolagem automatica da pagina)
export function BotaoRolagem() {
  const botao = useRef<HTMLButtonElement>(null)
  const { rolando, rolavel, alternar } = useRolagemAutomatica(botao)

  if (!rolavel) return null

  return (
    <button
      ref={botao}
      type="button"
      className="botao-rolagem"
      onClick={alternar}
      aria-pressed={rolando}
      aria-label={rolando ? 'Parar a rolagem automatica' : 'Rolar a pagina sozinha para ler'}
      title={rolando ? 'Parar a rolagem automatica' : 'Rolar a pagina sozinha para ler'}
    >
      {rolando ? 'Parar' : 'Rolar'}
    </button>
  )
}
