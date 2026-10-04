import { useTema } from '../hooks/useTema.ts'

function IconeLua() {
  return (
    <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true">
      <path d="M12.1 22a10 10 0 0 1-6.7-3.4A10 10 0 0 1 9.6 2.2a1 1 0 0 1 1.2 1.3 8 8 0 0 0 10 10.2 1 1 0 0 1 1.1 1.4A10 10 0 0 1 12.1 22z" />
    </svg>
  )
}

function IconeSol() {
  return (
    <svg
      viewBox="0 0 24 24"
      width="22"
      height="22"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
  )
}

export function BotaoTema() {
  const { tema, alternar } = useTema()
  const rotulo = tema === 'claro' ? 'Ativar tema escuro' : 'Ativar tema claro'

  return (
    <button type="button" className="botao-tema" onClick={alternar} aria-label={rotulo} title={rotulo}>
      {tema === 'claro' ? <IconeLua /> : <IconeSol />}
    </button>
  )
}
