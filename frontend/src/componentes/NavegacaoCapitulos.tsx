import { Link } from 'react-router-dom'
import type { Livro } from '../api/tipos.ts'
import { caminhoDoCapitulo, vizinhos } from '../utils/capitulos.ts'
import type { Posicao } from '../utils/capitulos.ts'

interface NavegacaoCapitulosProps {
  livros: Livro[]
  livro: string
  capitulo: number
}

function Botao({ alvo, rotulo }: { alvo: Posicao | null; rotulo: string }) {
  if (!alvo) {
    // no primeiro e no ultimo capitulo da Biblia o botao fica, mas desabilitado
    return (
      <span className="botao-secundario botao-largo desabilitado" role="link" aria-disabled="true">
        {rotulo}
      </span>
    )
  }
  return (
    <Link className="botao-secundario botao-largo" to={caminhoDoCapitulo(alvo)}>
      {rotulo}
    </Link>
  )
}

export function NavegacaoCapitulos({ livros, livro, capitulo }: NavegacaoCapitulosProps) {
  const { anterior, proximo } = vizinhos(livros, livro, capitulo)

  return (
    <nav className="navegacao-capitulos" aria-label="Navegacao entre capitulos">
      <Botao alvo={anterior} rotulo="Capitulo anterior" />
      <Botao alvo={proximo} rotulo="Proximo capitulo" />
    </nav>
  )
}
