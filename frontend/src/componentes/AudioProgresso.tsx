import { formatarTempo, useFalaProgresso } from '../hooks/useFalaProgresso.ts'

function IconeTocar() {
  return (
    <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" aria-hidden="true">
      <path d="M8 5v14l11-7z" />
    </svg>
  )
}

function IconePausar() {
  return (
    <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" aria-hidden="true">
      <rect x="6" y="5" width="4" height="14" />
      <rect x="14" y="5" width="4" height="14" />
    </svg>
  )
}

// Ouvir o capitulo inteiro, com pausa e tempo (decorrido / estimado)
export function AudioProgresso({ texto }: { texto: string }) {
  const { suportado, estado, decorrido, total, alternar } = useFalaProgresso(texto)

  if (!suportado) return null

  const rotulo = estado === 'falando' ? 'Pausar' : estado === 'pausado' ? 'Continuar' : 'Ouvir capitulo'

  return (
    <div className="audio-progresso">
      <button type="button" className="botao-icone" onClick={alternar} aria-label={rotulo} title={rotulo}>
        {estado === 'falando' ? <IconePausar /> : <IconeTocar />}
      </button>
      {estado !== 'parado' && (
        <span className="texto-mutado tempo-audio">
          {formatarTempo(decorrido)} / {formatarTempo(total)}
        </span>
      )}
    </div>
  )
}
