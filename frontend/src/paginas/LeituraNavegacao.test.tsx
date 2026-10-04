import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { BuscaProvider } from '../contexto/BuscaProvider.tsx'
import { Home } from './Home.tsx'
import { Leitura } from './Leitura.tsx'

function json(corpo: unknown, status = 200) {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

const LIVROS = [
  { livro: 'Genesis', indice_inicial: 0, total_capitulos: 3 },
  { livro: 'São Lucas', indice_inicial: 3, total_capitulos: 2 },
]

function capitulo(livro: string, numero: number) {
  return {
    livro,
    capitulo: numero,
    total_capitulos_livro: LIVROS.find((l) => l.livro === livro)!.total_capitulos,
    versiculos: [{ versiculo: 1, texto: `Texto de ${livro} ${numero}.` }],
  }
}

let falhaNaLista = false

beforeEach(() => {
  falhaNaLista = false
  vi.stubGlobal(
    'fetch',
    vi.fn((caminho: string) => {
      if (caminho.startsWith('/api/livros')) {
        return Promise.resolve(falhaNaLista ? json({ detail: 'erro' }, 500) : json(LIVROS))
      }
      if (caminho.startsWith('/api/versiculo-do-dia')) {
        return Promise.resolve(json({ referencia: 'Gn 1,1', texto: 'x', data: '2026-10-04' }))
      }
      const m = decodeURIComponent(caminho).match(/^\/api\/capitulos\/(.+)\/(\d+)$/)
      if (m) return Promise.resolve(json(capitulo(m[1], Number(m[2]))))
      return Promise.resolve(json({ detail: 'nao encontrado' }, 404))
    }),
  )
})

afterEach(() => vi.unstubAllGlobals())

function Local() {
  return <span data-testid="local">{decodeURIComponent(useLocation().pathname)}</span>
}

function renderizar(caminho: string) {
  return render(
    <MemoryRouter initialEntries={[caminho]}>
      <BuscaProvider>
        <Routes>
          <Route path="/ler/:livro/:capitulo" element={<Leitura />} />
          <Route path="/" element={<Home />} />
        </Routes>
        <Local />
      </BuscaProvider>
    </MemoryRouter>,
  )
}

describe('navegacao entre capitulos', () => {
  it('mostra os botoes anterior e proximo no meio do livro', async () => {
    renderizar('/ler/Genesis/2')
    await screen.findByText('Texto de Genesis 2.')

    expect(await screen.findByRole('link', { name: 'Capitulo anterior' })).toHaveAttribute('href', '/ler/Genesis/1')
    expect(screen.getByRole('link', { name: 'Proximo capitulo' })).toHaveAttribute('href', '/ler/Genesis/3')
  })

  it('no ultimo capitulo do livro o proximo leva ao primeiro do seguinte', async () => {
    renderizar('/ler/Genesis/3')
    await screen.findByText('Texto de Genesis 3.')

    expect(await screen.findByRole('link', { name: 'Proximo capitulo' })).toHaveAttribute(
      'href',
      '/ler/S%C3%A3o%20Lucas/1',
    )
  })

  it('no primeiro capitulo da Biblia o botao anterior fica desabilitado, sem link', async () => {
    renderizar('/ler/Genesis/1')
    await screen.findByText('Texto de Genesis 1.')
    await screen.findByRole('link', { name: 'Proximo capitulo' })

    const anterior = screen.getByText('Capitulo anterior')
    expect(anterior).toHaveAttribute('aria-disabled', 'true')
    expect(anterior.closest('a')).toBeNull()
  })

  it('no ultimo capitulo da Biblia o botao proximo fica desabilitado', async () => {
    renderizar('/ler/S%C3%A3o%20Lucas/2')
    await screen.findByText('Texto de São Lucas 2.')
    await screen.findByRole('link', { name: 'Capitulo anterior' })

    expect(screen.getByText('Proximo capitulo')).toHaveAttribute('aria-disabled', 'true')
  })

  it('clicar em proximo abre o capitulo seguinte e leva a pagina ao topo', async () => {
    renderizar('/ler/Genesis/1')
    fireEvent.click(await screen.findByRole('link', { name: 'Proximo capitulo' }))

    expect(await screen.findByText('Texto de Genesis 2.')).toBeInTheDocument()
    expect(screen.getByTestId('local')).toHaveTextContent('/ler/Genesis/2')
    expect(window.scrollTo).toHaveBeenLastCalledWith(0, 0)
  })

  it('abrir um capitulo tambem rola a pagina para o topo', async () => {
    renderizar('/ler/Genesis/1')
    await screen.findByText('Texto de Genesis 1.')

    expect(window.scrollTo).toHaveBeenCalledWith(0, 0)
  })

  it('se a lista de livros falhar, a leitura segue sem os botoes de navegacao', async () => {
    falhaNaLista = true
    renderizar('/ler/Genesis/2')

    expect(await screen.findByText('Texto de Genesis 2.')).toBeInTheDocument()
    await waitFor(() => expect(fetch).toHaveBeenCalledWith('/api/livros', undefined))
    expect(screen.queryByRole('navigation', { name: 'Navegacao entre capitulos' })).not.toBeInTheDocument()
  })
})

describe('rodape da tela inicial', () => {
  it('mostra autoria e licenca com links externos seguros', async () => {
    renderizar('/')

    const autor = await screen.findByRole('link', { name: 'Armando Netto' })
    expect(autor).toHaveAttribute('href', 'https://armandonetto.com/')
    expect(autor).toHaveAttribute('target', '_blank')
    expect(autor).toHaveAttribute('rel', expect.stringContaining('noopener'))
    expect(screen.getByRole('link', { name: 'Licenca Verbo 1.0' })).toHaveAttribute(
      'href',
      'https://github.com/armandonettox/verbo/blob/master/LICENSE',
    )
  })
})
