import { useState } from 'react'
import { Link } from 'react-router-dom'
import type { Versiculo } from '../api/tipos.ts'
import { resumirTexto } from '../utils/texto.ts'

const POR_PAGINA = 4

interface BarraResultadosProps {
  versiculos: Versiculo[]
  onNovaBusca: () => void
}

export function BarraResultados({ versiculos, onNovaBusca }: BarraResultadosProps) {
  const [visiveis, setVisiveis] = useState(POR_PAGINA)

  return (
    <section className="cartao" aria-label="Versiculos encontrados">
      <p className="rotulo-cartao">VERSICULOS ENCONTRADOS</p>
      <button type="button" className="botao-secundario botao-largo" onClick={onNovaBusca}>
        Nova busca
      </button>

      <ul className="lista-versiculos">
        {versiculos.slice(0, visiveis).map((v) => (
          <li key={v.referencia} className="cartao cartao-versiculo">
            <strong>{v.referencia}</strong>
            {v.similaridade !== null && (
              <span className="texto-mutado similaridade">{v.similaridade.toFixed(2)}% similar</span>
            )}
            {v.livro && v.capitulo !== null && (
              <Link
                className="botao-secundario botao-largo"
                to={`/ler/${encodeURIComponent(v.livro)}/${v.capitulo}`}
              >
                Ver versiculo
              </Link>
            )}
            <p>{resumirTexto(v.texto)}</p>
          </li>
        ))}
      </ul>

      {visiveis < versiculos.length && (
        <button
          type="button"
          className="botao-secundario botao-largo"
          onClick={() => setVisiveis((n) => n + POR_PAGINA)}
        >
          Mostrar mais resultados
        </button>
      )}
    </section>
  )
}
