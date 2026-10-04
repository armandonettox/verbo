import { useFala } from '../hooks/useFala.ts'

interface BotaoAudioProps {
  texto: string
}

function IconeAltoFalante() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">
      <path d="M3 10v4h4l5 5V5L7 10H3z" />
      <path d="M16.5 12c0-1.77-1-3.29-2.5-4.03v8.05c1.5-.73 2.5-2.25 2.5-4.02z" />
    </svg>
  )
}

function IconeParar() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">
      <rect x="6" y="6" width="12" height="12" />
    </svg>
  )
}

// Botao so com icone: ouvir o texto ou parar a leitura em andamento
export function BotaoAudio({ texto }: BotaoAudioProps) {
  const { suportado, falando, falar, parar } = useFala()

  // Navegadores sem voz sintetizada nao mostram um botao que nao funciona
  if (!suportado) return null

  const rotulo = falando ? 'Parar audio' : 'Ouvir'

  return (
    <button
      type="button"
      className="botao-icone"
      onClick={() => (falando ? parar() : falar(texto))}
      aria-label={rotulo}
      title={rotulo}
    >
      {falando ? <IconeParar /> : <IconeAltoFalante />}
    </button>
  )
}
