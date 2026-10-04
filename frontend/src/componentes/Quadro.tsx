import type { ReactNode } from 'react'

interface QuadroProps {
  barra: ReactNode
  children: ReactNode
}

// Estrutura das telas: barra lateral de 380px mais a area de conteudo
export function Quadro({ barra, children }: QuadroProps) {
  return (
    <div className="quadro">
      <aside className="barra-lateral">{barra}</aside>
      <main className="conteudo">
        <div className="conteudo-miolo">{children}</div>
      </main>
    </div>
  )
}
