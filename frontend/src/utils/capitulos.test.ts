import { describe, expect, it } from 'vitest'
import type { Livro } from '../api/tipos.ts'
import { caminhoDoCapitulo, vizinhos } from './capitulos.ts'

const LIVROS: Livro[] = [
  { livro: 'Genesis', indice_inicial: 0, total_capitulos: 3 },
  { livro: 'Exodo', indice_inicial: 3, total_capitulos: 2 },
  { livro: 'São Lucas', indice_inicial: 5, total_capitulos: 4 },
]

describe('vizinhos', () => {
  it('no meio do livro anda um capitulo para cada lado', () => {
    expect(vizinhos(LIVROS, 'Genesis', 2)).toEqual({
      anterior: { livro: 'Genesis', capitulo: 1 },
      proximo: { livro: 'Genesis', capitulo: 3 },
    })
  })

  it('no ultimo capitulo de um livro o proximo e o primeiro do seguinte', () => {
    expect(vizinhos(LIVROS, 'Genesis', 3).proximo).toEqual({ livro: 'Exodo', capitulo: 1 })
  })

  it('no primeiro capitulo de um livro o anterior e o ultimo do livro de antes', () => {
    expect(vizinhos(LIVROS, 'Exodo', 1).anterior).toEqual({ livro: 'Genesis', capitulo: 3 })
    expect(vizinhos(LIVROS, 'São Lucas', 1).anterior).toEqual({ livro: 'Exodo', capitulo: 2 })
  })

  it('no inicio da Biblia nao ha anterior e no fim nao ha proximo', () => {
    expect(vizinhos(LIVROS, 'Genesis', 1).anterior).toBeNull()
    expect(vizinhos(LIVROS, 'São Lucas', 4).proximo).toBeNull()
  })

  it('o primeiro capitulo ainda tem proximo e o ultimo ainda tem anterior', () => {
    expect(vizinhos(LIVROS, 'Genesis', 1).proximo).toEqual({ livro: 'Genesis', capitulo: 2 })
    expect(vizinhos(LIVROS, 'São Lucas', 4).anterior).toEqual({ livro: 'São Lucas', capitulo: 3 })
  })

  it.each([
    ['livro desconhecido', 'Inexistente', 1],
    ['capitulo zero', 'Genesis', 0],
    ['capitulo alem do total', 'Genesis', 4],
    ['capitulo fracionado', 'Genesis', 1.5],
  ])('%s nao tem vizinhos', (_, livro, capitulo) => {
    expect(vizinhos(LIVROS, livro, capitulo)).toEqual({ anterior: null, proximo: null })
  })

  it('lista vazia nao quebra', () => {
    expect(vizinhos([], 'Genesis', 1)).toEqual({ anterior: null, proximo: null })
  })
})

describe('caminhoDoCapitulo', () => {
  it('codifica o nome do livro com acento e espaco', () => {
    expect(caminhoDoCapitulo({ livro: 'São Lucas', capitulo: 11 })).toBe('/ler/S%C3%A3o%20Lucas/11')
  })
})
