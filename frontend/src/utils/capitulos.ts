import type { Livro } from '../api/tipos.ts'

export interface Posicao {
  livro: string
  capitulo: number
}

export interface Vizinhos {
  anterior: Posicao | null
  proximo: Posicao | null
}

// Capitulo anterior e proximo na ordem da Biblia: ao passar do ultimo capitulo de um livro
// vai para o primeiro do seguinte, e o inverso para voltar. Nulo no inicio e no fim da Biblia.
export function vizinhos(livros: Livro[], livro: string, capitulo: number): Vizinhos {
  const i = livros.findIndex((l) => l.livro === livro)
  const nenhum: Vizinhos = { anterior: null, proximo: null }
  if (i < 0) return nenhum
  const total = livros[i].total_capitulos
  if (!Number.isInteger(capitulo) || capitulo < 1 || capitulo > total) return nenhum

  let anterior: Posicao | null = null
  if (capitulo > 1) anterior = { livro, capitulo: capitulo - 1 }
  else if (i > 0) anterior = { livro: livros[i - 1].livro, capitulo: livros[i - 1].total_capitulos }

  let proximo: Posicao | null = null
  if (capitulo < total) proximo = { livro, capitulo: capitulo + 1 }
  else if (i < livros.length - 1) proximo = { livro: livros[i + 1].livro, capitulo: 1 }

  return { anterior, proximo }
}

export function caminhoDoCapitulo({ livro, capitulo }: Posicao): string {
  return `/ler/${encodeURIComponent(livro)}/${capitulo}`
}
