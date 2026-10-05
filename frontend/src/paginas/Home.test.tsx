import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { BuscaProvider } from '../contexto/BuscaProvider.tsx'
import { Home } from './Home.tsx'

function json(corpo: unknown, status = 200) {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

const VERSICULO_DIA = {
  referencia: 'Genesis 1,1',
  texto: 'No principio Deus criou o ceu e a terra.',
  data: '2026-10-03',
}

const RESPOSTA = { resposta: 'Jesus ensinou o Pai Nosso.' }

const RESULTADO = {
  pergunta: 'como orar?',
  modo: 'nvidia',
  aviso: null,
  versiculos: [
    { referencia: 'Sao Lucas 11:1-12', texto: 'Senhor, ensina-nos a orar.', similaridade: 66.3, livro: 'Sao Lucas', capitulo: 11 },
  ],
}

// Responde cada rota com o corpo combinado
function simularApi(rotasDoTeste: Record<string, () => Response>) {
  const rotas: Record<string, () => Response> = { '/api/livros': () => json([]), ...rotasDoTeste }
  vi.stubGlobal(
    'fetch',
    vi.fn((caminho: string) => {
      const rota = Object.keys(rotas).find((r) => caminho.startsWith(r))
      if (!rota) return Promise.reject(new Error(`rota nao simulada: ${caminho}`))
      return Promise.resolve(rotas[rota]())
    }),
  )
}

function renderizar() {
  return render(
    <MemoryRouter>
      <BuscaProvider>
        <Home />
      </BuscaProvider>
    </MemoryRouter>,
  )
}

function buscarPor(pergunta: string) {
  fireEvent.change(screen.getByLabelText('Qual e a sua pergunta?'), { target: { value: pergunta } })
  fireEvent.click(screen.getByRole('button', { name: 'Buscar' }))
}

beforeEach(() => {
  simularApi({ '/api/versiculo-do-dia': () => json(VERSICULO_DIA) })
})

afterEach(() => vi.unstubAllGlobals())

describe('Home', () => {
  it('mostra a leitura do dia vinda da API', async () => {
    renderizar()

    expect(await screen.findByText('Genesis 1,1')).toBeInTheDocument()
    expect(screen.getByText('No principio Deus criou o ceu e a terra.')).toBeInTheDocument()
  })

  it('esconde o cartao do dia se a API falhar, sem quebrar a tela', async () => {
    simularApi({ '/api/versiculo-do-dia': () => json({ detail: 'erro' }, 500) })

    renderizar()

    await waitFor(() => expect(screen.queryByText('Carregando...')).not.toBeInTheDocument())
    expect(screen.queryByText('LEITURA DO DIA')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Buscar' })).toBeInTheDocument()
  })

  it('busca e mostra a resposta e o versiculo na barra lateral', async () => {
    simularApi({
      '/api/versiculo-do-dia': () => json(VERSICULO_DIA),
      '/api/versiculos': () => json(RESULTADO),
      '/api/resposta': () => json(RESPOSTA),
    })
    renderizar()

    buscarPor('como orar?')

    expect(await screen.findByText('Jesus ensinou o Pai Nosso.')).toBeInTheDocument()
    expect(screen.getByText('Sao Lucas 11:1-12')).toBeInTheDocument()
    expect(screen.getByText('66.30% similar')).toBeInTheDocument()
  })

  it('mostra o aviso do modo local sem resposta gerada', async () => {
    simularApi({
      '/api/versiculo-do-dia': () => json(VERSICULO_DIA),
      '/api/versiculos': () =>
        json({ ...RESULTADO, modo: 'local', aviso: 'Mostrando uma busca simplificada.' }),
    })
    renderizar()

    buscarPor('como orar?')

    expect(await screen.findByRole('status')).toHaveTextContent('busca simplificada')
    expect(screen.queryByText('Jesus ensinou o Pai Nosso.')).not.toBeInTheDocument()
  })

  it('mostra o erro da API e permanece na tela de busca', async () => {
    simularApi({
      '/api/versiculo-do-dia': () => json(VERSICULO_DIA),
      '/api/versiculos': () => json({ detail: 'O servico de IA esta indisponivel.' }, 503),
    })
    renderizar()

    buscarPor('como orar?')

    expect(await screen.findByRole('alert')).toHaveTextContent('O servico de IA esta indisponivel.')
    expect(screen.getByRole('button', { name: 'Buscar' })).toBeEnabled()
  })

  it('Nova busca volta para a tela inicial', async () => {
    simularApi({
      '/api/versiculo-do-dia': () => json(VERSICULO_DIA),
      '/api/versiculos': () => json(RESULTADO),
      '/api/resposta': () => json(RESPOSTA),
    })
    renderizar()
    buscarPor('como orar?')
    await screen.findByText('Jesus ensinou o Pai Nosso.')

    fireEvent.click(screen.getByRole('button', { name: 'Nova busca' }))

    expect(await screen.findByLabelText('Qual e a sua pergunta?')).toBeInTheDocument()
  })
})
