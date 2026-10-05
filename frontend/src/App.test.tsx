import { render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App.tsx'

function json(corpo: unknown) {
  return new Response(JSON.stringify(corpo), { status: 200, headers: { 'Content-Type': 'application/json' } })
}

// Monta o App de verdade (com as rotas reais) em cada endereco, como o navegador faria
beforeEach(() => {
  vi.stubGlobal(
    'fetch',
    vi.fn((caminho: string, opcoes?: RequestInit) => {
      if (caminho === '/api/versiculos') {
        const { pergunta } = JSON.parse(opcoes!.body as string)
        return Promise.resolve(json({ pergunta, modo: 'nvidia', aviso: null, versiculos: [] }))
      }
      if (caminho.startsWith('/api/versiculo-do-dia')) {
        return Promise.resolve(json({ referencia: 'Gn 1,1', texto: 'x', data: '2026-10-05' }))
      }
      return Promise.resolve(json([]))
    }),
  )
})

afterEach(() => {
  vi.unstubAllGlobals()
  window.history.pushState({}, '', '/')
})

describe('rotas do App', () => {
  it('/ mostra a tela inicial', async () => {
    window.history.pushState({}, '', '/')
    render(<App />)
    expect(await screen.findByLabelText('Qual e a sua pergunta?')).toBeInTheDocument()
  })

  it('/buscar?q=... abre a busca (a rota existe)', async () => {
    window.history.pushState({}, '', '/buscar?q=como%20orar%3F')
    render(<App />)

    // sem a rota nada renderizava: nem o botao de tema aparecia
    expect(await screen.findByRole('button', { name: /tema/i })).toBeInTheDocument()
    expect(await screen.findByText('como orar?', { selector: 'p' })).toBeInTheDocument()
  })

  it('/buscar sem pergunta cai na tela inicial', async () => {
    window.history.pushState({}, '', '/buscar')
    render(<App />)
    expect(await screen.findByLabelText('Qual e a sua pergunta?')).toBeInTheDocument()
    expect(window.location.pathname).toBe('/')
  })
})
