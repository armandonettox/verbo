import { useState } from 'react'
import { limparHistorico, lerHistorico } from '../utils/historico.ts'

interface HistoricoBuscasProps {
  onBuscar: (pergunta: string) => void
}

// As ultimas buscas, guardadas so neste navegador. Tocar numa delas refaz a busca.
export function HistoricoBuscas({ onBuscar }: HistoricoBuscasProps) {
  const [perguntas, setPerguntas] = useState(lerHistorico)

  if (perguntas.length === 0) return null

  function limpar() {
    limparHistorico()
    setPerguntas([])
  }

  return (
    <section className="historico-buscas" aria-label="Buscas recentes">
      <p className="rotulo-cartao">BUSCAS RECENTES</p>
      <ul className="lista-historico">
        {perguntas.map((pergunta) => (
          <li key={pergunta}>
            <button type="button" className="botao-historico" onClick={() => onBuscar(pergunta)}>
              {pergunta}
            </button>
          </li>
        ))}
      </ul>
      <button type="button" className="botao-secundario botao-largo" onClick={limpar}>
        Limpar historico
      </button>
      <p className="texto-mutado aviso-historico">Guardado so neste navegador.</p>
    </section>
  )
}
