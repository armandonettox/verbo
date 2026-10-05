import type { ReactNode } from 'react'
import { useBarraLateral } from '../hooks/useBarraLateral.ts'

interface QuadroProps {
  barra: ReactNode
  children: ReactNode
  // Em tela estreita a barra e uma gaveta fechada; com este texto aparece um botao no
  // conteudo que abre a gaveta (por exemplo, para ver os versiculos encontrados)
  rotuloVersiculos?: string
}

function IconeBarra() {
  return (
    <svg
      viewBox="0 0 24 24"
      width="22"
      height="22"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <path d="M9 4v16" />
    </svg>
  )
}

// Estrutura das telas: barra lateral que abre e fecha mais a area de conteudo
export function Quadro({ barra, children, rotuloVersiculos }: QuadroProps) {
  const { aberta, estreita, alternar, fechar } = useBarraLateral()
  const rotulo = aberta ? 'Fechar barra lateral' : 'Abrir barra lateral'

  return (
    <div className={aberta ? 'quadro' : 'quadro barra-fechada'}>
      <button
        type="button"
        className="botao-barra"
        onClick={alternar}
        aria-expanded={aberta}
        aria-controls="barra-lateral"
        aria-label={rotulo}
        title={rotulo}
      >
        <IconeBarra />
        {/* o nome acessivel continua sendo o aria-label; o texto so torna o botao facil de achar */}
        <span className="botao-barra-texto" aria-hidden="true">
          {aberta ? 'Fechar barra' : 'Abrir barra'}
        </span>
      </button>
      {estreita && aberta && <div className="barra-fundo" onClick={fechar} aria-hidden="true" />}
      {/* inert tira a barra fechada da navegacao por teclado e dos leitores de tela */}
      <aside id="barra-lateral" className="barra-lateral" inert={!aberta}>
        {barra}
      </aside>
      <main className="conteudo">
        <div className="conteudo-miolo">
          {rotuloVersiculos && estreita && !aberta && (
            <button type="button" className="botao-secundario botao-largo" onClick={alternar}>
              {rotuloVersiculos}
            </button>
          )}
          {children}
        </div>
      </main>
    </div>
  )
}
