import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import type { Versiculo } from '../api/tipos.ts'
import { resumirTexto } from '../utils/texto.ts'

const POR_PAGINA = 4

interface BarraResultadosProps {
  pergunta: string
  versiculos: Versiculo[]
  onNovaBusca: () => void
}

export function BarraResultados({ pergunta, versiculos, onNovaBusca }: BarraResultadosProps) {
  const [visiveis, setVisiveis] = useState(POR_PAGINA)
  const [copia, setCopia] = useState<'nada' | 'copiado' | 'falhou'>('nada')
  const temporizador = useRef<number | undefined>(undefined)

  useEffect(() => () => window.clearTimeout(temporizador.current), [])

  async function copiarLink() {
    const endereco = `${window.location.origin}/buscar?q=${encodeURIComponent(pergunta)}`
    try {
      await navigator.clipboard.writeText(endereco)
      setCopia('copiado')
    } catch {
      setCopia('falhou')
    }
    window.clearTimeout(temporizador.current)
    temporizador.current = window.setTimeout(() => setCopia('nada'), 2500)
  }

  return (
    <section className="cartao" aria-label="Versiculos encontrados">
      <p className="rotulo-cartao">VERSICULOS ENCONTRADOS</p>
      <button type="button" className="botao-secundario botao-largo" onClick={onNovaBusca}>
        Nova busca
      </button>
      <button type="button" className="botao-secundario botao-largo" onClick={copiarLink}>
        Copiar link da busca
      </button>
      {copia !== 'nada' && (
        <p className="texto-mutado aviso-link" role="status">
          {copia === 'copiado'
            ? 'Link copiado.'
            : 'Nao foi possivel copiar. Copie o endereco da barra do navegador.'}
        </p>
      )}

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
