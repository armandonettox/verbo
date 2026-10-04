import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listarLivros } from '../api/cliente.ts'
import type { Livro } from '../api/tipos.ts'

interface SeletorCapituloProps {
  livroInicial?: string
  capituloInicial?: number
}

export function SeletorCapitulo({ livroInicial, capituloInicial }: SeletorCapituloProps) {
  const navegar = useNavigate()
  const [livros, setLivros] = useState<Livro[]>([])
  const [indisponivel, setIndisponivel] = useState(false)
  const [livro, setLivro] = useState(livroInicial ?? '')
  const [capitulo, setCapitulo] = useState(capituloInicial ?? 1)

  useEffect(() => {
    let cancelado = false
    async function carregar() {
      try {
        const lista = await listarLivros()
        if (cancelado) return
        setLivros(lista)
        // sem livro de partida, comeca no primeiro
        setLivro((atual) => atual || lista[0]?.livro || '')
      } catch {
        if (!cancelado) setIndisponivel(true)
      }
    }
    carregar()
    return () => {
      cancelado = true
    }
  }, [])

  if (indisponivel) {
    return <p className="texto-mutado">Nao foi possivel carregar a lista de livros.</p>
  }

  const atual = livros.find((l) => l.livro === livro)
  const totalCapitulos = atual?.total_capitulos ?? 1

  function trocarLivro(nome: string) {
    setLivro(nome)
    setCapitulo(1)
  }

  function comecarLeitura() {
    if (!atual) return
    navegar(`/ler/${encodeURIComponent(atual.livro)}/${capitulo}`)
  }

  return (
    <section className="cartao" aria-label="Escolha o livro e capitulo">
      <p className="rotulo-cartao">ESCOLHA O LIVRO E CAPITULO</p>

      <label className="campo-seletor">
        Livro
        <select value={livro} onChange={(e) => trocarLivro(e.target.value)} disabled={livros.length === 0}>
          {livros.map((l) => (
            <option key={l.livro} value={l.livro}>
              {l.livro}
            </option>
          ))}
        </select>
      </label>

      <label className="campo-seletor">
        Capitulo
        <select
          value={capitulo}
          onChange={(e) => setCapitulo(Number(e.target.value))}
          disabled={livros.length === 0}
        >
          {Array.from({ length: totalCapitulos }, (_, i) => i + 1).map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </label>

      <button
        type="button"
        className="botao-secundario botao-largo"
        onClick={comecarLeitura}
        disabled={!atual}
      >
        Comecar leitura
      </button>
    </section>
  )
}
