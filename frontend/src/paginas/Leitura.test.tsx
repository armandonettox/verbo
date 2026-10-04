import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { BuscaProvider } from '../contexto/BuscaProvider.tsx'
import { Leitura } from './Leitura.tsx'

function json(corpo: unknown, status = 200) {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

const LIVROS = [
  { livro: 'Genesis', indice_inicial: 0, total_capitulos: 3 },
  { livro: 'São Lucas', indice_inicial: 3, total_capitulos: 24 },
]

const GENESIS_1 = {
  livro: 'Genesis',
  capitulo: 1,
  total_capitulos_livro: 3,
  versiculos: [
    { versiculo: 1, texto: 'No principio Deus criou o ceu e a terra.' },
    { versiculo: 2, texto: 'A terra estava informe e vazia.' },
  ],
}

let rotas: Record<string, () => Response>

beforeEach(() => {
  rotas = {
    '/api/livros': () => json(LIVROS),
    '/api/capitulos/Genesis/1': () => json(GENESIS_1),
  }
  vi.stubGlobal(
    'fetch',
    vi.fn((caminho: string) => {
      const chave = Object.keys(rotas).find((r) => caminho.startsWith(r))
      if (!chave) return Promise.resolve(json({ detail: 'Capitulo nao encontrado.' }, 404))
      return Promise.resolve(rotas[chave]())
    }),
  )
})

afterEach(() => vi.unstubAllGlobals())

function Local() {
  return <span data-testid="local">{useLocation().pathname}</span>
}

function renderizar(caminho: string) {
  return render(
    <MemoryRouter initialEntries={[caminho]}>
      <BuscaProvider>
        <Routes>
          <Route path="/ler/:livro/:capitulo" element={<Leitura />} />
          <Route path="/" element={<p>inicio</p>} />
        </Routes>
        <Local />
      </BuscaProvider>
    </MemoryRouter>,
  )
}

describe('Leitura', () => {
  it('mostra o titulo e os versiculos numerados', async () => {
    renderizar('/ler/Genesis/1')

    expect(await screen.findByRole('heading', { name: 'Genesis 1' })).toBeInTheDocument()
    expect(screen.getByText('No principio Deus criou o ceu e a terra.')).toBeInTheDocument()
    expect(screen.getByText('2.')).toBeInTheDocument()
  })

  it('mostra carregando enquanto busca o capitulo', () => {
    renderizar('/ler/Genesis/1')

    expect(screen.getByRole('status')).toHaveTextContent('Carregando')
  })

  it('capitulo inexistente mostra o erro, sem quebrar', async () => {
    renderizar('/ler/Genesis/99')

    expect(await screen.findByRole('alert')).toHaveTextContent('Capitulo nao encontrado.')
  })

  it('numero invalido na URL nem chama a API de capitulo', async () => {
    renderizar('/ler/Genesis/abc')

    expect(await screen.findByRole('alert')).toHaveTextContent('Capitulo nao encontrado.')
    const chamadas = vi.mocked(fetch).mock.calls.map(([c]) => String(c))
    expect(chamadas.some((c) => c.startsWith('/api/capitulos'))).toBe(false)
  })

  it('erro de servidor mostra a mensagem da API', async () => {
    rotas['/api/capitulos/Genesis/1'] = () => json({ detail: 'Servidor com problema.' }, 500)

    renderizar('/ler/Genesis/1')

    expect(await screen.findByRole('alert')).toHaveTextContent('Servidor com problema.')
  })

  it('Voltar para busca vai para a tela inicial', async () => {
    renderizar('/ler/Genesis/1')
    await screen.findByRole('heading', { name: 'Genesis 1' })

    fireEvent.click(screen.getByRole('link', { name: 'Voltar para busca' }))

    expect(await screen.findByText('inicio')).toBeInTheDocument()
  })

  it('o seletor abre ja no livro e capitulo atuais', async () => {
    renderizar('/ler/Genesis/1')

    await waitFor(() => expect(screen.getByLabelText('Livro')).toHaveValue('Genesis'))
    expect(screen.getByLabelText('Capitulo')).toHaveValue('1')
  })

  it('trocar o livro volta o capitulo para 1 e limita ao total do livro', async () => {
    renderizar('/ler/Genesis/1')
    await screen.findByRole('heading', { name: 'Genesis 1' })
    await waitFor(() => expect(screen.getByLabelText('Livro')).toHaveValue('Genesis'))
    expect(screen.getByLabelText('Capitulo').querySelectorAll('option')).toHaveLength(3)

    fireEvent.change(screen.getByLabelText('Livro'), { target: { value: 'São Lucas' } })

    expect(screen.getByLabelText('Capitulo')).toHaveValue('1')
    expect(screen.getByLabelText('Capitulo').querySelectorAll('option')).toHaveLength(24)
  })

  it('Comecar leitura navega com o livro codificado na URL', async () => {
    renderizar('/ler/Genesis/1')
    await waitFor(() => expect(screen.getByLabelText('Livro')).toHaveValue('Genesis'))

    fireEvent.change(screen.getByLabelText('Livro'), { target: { value: 'São Lucas' } })
    fireEvent.change(screen.getByLabelText('Capitulo'), { target: { value: '11' } })
    fireEvent.click(screen.getByRole('button', { name: 'Comecar leitura' }))

    expect(screen.getByTestId('local')).toHaveTextContent('/ler/S%C3%A3o%20Lucas/11')
  })
})
