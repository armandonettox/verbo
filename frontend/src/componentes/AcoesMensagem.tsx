import { useEffect, useRef, useState } from 'react'
import { textoSemMarkdown } from '../utils/texto.ts'
import { BotaoAudio } from './BotaoAudio.tsx'

interface AcoesMensagemProps {
  markdown: string
  onRegenerar?: () => void
  desabilitado?: boolean
}

const icone = {
  viewBox: '0 0 24 24',
  width: 20,
  height: 20,
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true,
}

function IconeCopiar() {
  return (
    <svg {...icone}>
      <rect x="9" y="9" width="12" height="12" rx="2" />
      <path d="M5 15V5a2 2 0 0 1 2-2h10" />
    </svg>
  )
}

function IconeConfirmado() {
  return (
    <svg {...icone}>
      <path d="M5 12l5 5L20 7" />
    </svg>
  )
}

function IconeCompartilhar() {
  return (
    <svg {...icone}>
      <circle cx="18" cy="5" r="3" />
      <circle cx="6" cy="12" r="3" />
      <circle cx="18" cy="19" r="3" />
      <path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4" />
    </svg>
  )
}

function IconeRegenerar() {
  return (
    <svg {...icone}>
      <path d="M20 11a8 8 0 0 0-14.9-3M4 5v4h4" />
      <path d="M4 13a8 8 0 0 0 14.9 3M20 19v-4h-4" />
    </svg>
  )
}

export function AcoesMensagem({ markdown, onRegenerar, desabilitado }: AcoesMensagemProps) {
  const texto = textoSemMarkdown(markdown)
  const [confirmado, setConfirmado] = useState(false)
  const temporizador = useRef<number | undefined>(undefined)

  useEffect(() => () => window.clearTimeout(temporizador.current), [])

  async function copiar() {
    try {
      await navigator.clipboard.writeText(texto)
    } catch {
      // clipboard pode estar bloqueado (pagina sem https ou permissao negada)
      return
    }
    setConfirmado(true)
    window.clearTimeout(temporizador.current)
    temporizador.current = window.setTimeout(() => setConfirmado(false), 1500)
  }

  async function compartilhar() {
    if (typeof navigator.share === 'function') {
      try {
        await navigator.share({ text: texto })
      } catch {
        // o usuario cancelou o compartilhamento
      }
      return
    }
    await copiar()
  }

  return (
    <div className="acoes-mensagem">
      <BotaoAudio texto={texto} />
      <button
        type="button"
        className="botao-icone"
        onClick={copiar}
        aria-label={confirmado ? 'Copiado' : 'Copiar resposta'}
        title="Copiar resposta"
      >
        {confirmado ? <IconeConfirmado /> : <IconeCopiar />}
      </button>
      <button
        type="button"
        className="botao-icone"
        onClick={compartilhar}
        aria-label="Compartilhar resposta"
        title="Compartilhar resposta"
      >
        <IconeCompartilhar />
      </button>
      {onRegenerar && (
        <button
          type="button"
          className="botao-icone"
          onClick={onRegenerar}
          disabled={desabilitado}
          aria-label="Gerar novamente"
          title="Gerar novamente"
        >
          <IconeRegenerar />
        </button>
      )}
    </div>
  )
}
