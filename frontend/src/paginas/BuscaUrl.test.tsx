import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { BuscaProvider } from '../contexto/BuscaProvider.tsx'
import { lerHistorico } from '../utils/historico.ts'
import { Home } from './Home.tsx'

function json(corpo: unknown, status = 200) {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

const VERSICULOS = [
  { referencia: 'Livro 1:1', texto: 'Texto um', similaridade: 50, livro: 'Livro', capitulo: 1 },
]

let chamadas: { caminho: string; corpo: Record<string, unknown> }[]

beforeEach(() => {
  chamadas = []
  vi.stubGlobal(
    'fetch',
    vi.fn((caminho: string, opcoes?: RequestInit) => {
      const corpo = opcoes?.body ? JSON.parse(opcoes.body as string) : {}
      chamadas.push({ caminho, corpo })
      if (caminho.startsWith('/api/livros')) return Promise.resolve(json([]))
      if (caminho.startsWith('/api/versiculo-do-dia')) {
        return Promise.resolve(json({ referencia: 'Gn 1,1', texto: 'x', data: '2026-10-05' }))
      }
      if (caminho === '/api/versiculos') {
        return Promise.resolve(
          json({ pergunta: corpo.pergunta, modo: 'nvidia', aviso: null, versiculos: VERSICULOS }),
        )
      }
      if (caminho === '/api/resposta') return Promise.resolve(json({ resposta: 'Resposta pronta.' }))
      return Promise.reject(new Error(`rota nao simulada: ${caminho}`))
    }),
  )
})

afterEach(() => vi.unstubAllGlobals())

function Endereco() {
  const { pathname, search } = useLocation()
  return <p data-testid="endereco">{pathname + search}</p>
}

// Simula voltar/abrir um endereco guardado nos favoritos
function IrPara({ destino }: { destino: string }) {
  const navegar = useNavigate()
  return (
    <button type="button" onClick={() => navegar(destino)}>
      ir para o endereco
    </button>
  )
}

function App({ inicial = '/', destino }: { inicial?: string; destino?: string }) {
  return (
    <MemoryRouter initialEntries={[inicial]}>
      <BuscaProvider>
        <Endereco />
        {destino && <IrPara destino={destino} />}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/buscar" element={<Home />} />
        </Routes>
      </BuscaProvider>
    </MemoryRouter>
  )
}

const buscasNaApi = () => chamadas.filter((c) => c.caminho === '/api/versiculos')

describe('endereco da busca', () => {
  it('abrir /buscar?q=... faz a busca uma vez so e mostra a conversa', async () => {
    render(<App inicial="/buscar?q=como%20orar%3F" />)

    expect(await screen.findByText('Resposta pronta.')).toBeInTheDocument()
    expect(buscasNaApi()).toHaveLength(1)
    expect(buscasNaApi()[0].corpo.pergunta).toBe('como orar?')
  })

  it('buscar pelo campo muda o endereco e nao busca duas vezes', async () => {
    render(<App />)

    fireEvent.change(screen.getByLabelText('Qual e a sua pergunta?'), { target: { value: 'o que e fe?' } })
    fireEvent.click(screen.getByRole('button', { name: 'Buscar' }))

    expect(await screen.findByText('Resposta pronta.')).toBeInTheDocument()
    expect(screen.getByTestId('endereco')).toHaveTextContent('/buscar?q=o%20que%20e%20fe%3F')
    expect(buscasNaApi()).toHaveLength(1)
  })

  it('depois de Nova busca, abrir de novo o mesmo endereco busca outra vez', async () => {
    render(<App inicial="/buscar?q=como%20orar%3F" destino="/buscar?q=como%20orar%3F" />)
    await screen.findByText('Resposta pronta.')
    fireEvent.click(screen.getByRole('button', { name: 'Nova busca' }))
    await screen.findByLabelText('Qual e a sua pergunta?')

    fireEvent.click(screen.getByRole('button', { name: 'ir para o endereco' }))

    await waitFor(() => expect(buscasNaApi()).toHaveLength(2))
    expect(await screen.findByText('Resposta pronta.')).toBeInTheDocument()
  })

  it('/buscar sem pergunta volta para a tela inicial', async () => {
    render(<App inicial="/buscar" />)

    expect(await screen.findByLabelText('Qual e a sua pergunta?')).toBeInTheDocument()
    expect(screen.getByTestId('endereco')).toHaveTextContent(/^\/$/)
    expect(buscasNaApi()).toHaveLength(0)
  })

  it('pergunta curta demais no endereco nao dispara busca', async () => {
    render(<App inicial="/buscar?q=a" />)

    expect(await screen.findByLabelText('Qual e a sua pergunta?')).toBeInTheDocument()
    expect(buscasNaApi()).toHaveLength(0)
  })

  it('Nova busca volta para / e limpa a conversa guardada', async () => {
    render(<App inicial="/buscar?q=como%20orar%3F" />)
    await screen.findByText('Resposta pronta.')

    fireEvent.click(screen.getByRole('button', { name: 'Nova busca' }))

    expect(await screen.findByLabelText('Qual e a sua pergunta?')).toBeInTheDocument()
    expect(screen.getByTestId('endereco')).toHaveTextContent(/^\/$/)
    expect(sessionStorage.getItem('verbo-conversa')).toBeNull()
  })
})

describe('conversa guardada na aba', () => {
  it('recarregar a pagina traz a conversa de volta sem buscar de novo', async () => {
    const primeira = render(<App inicial="/buscar?q=como%20orar%3F" />)
    await screen.findByText('Resposta pronta.')
    expect(buscasNaApi()).toHaveLength(1)
    primeira.unmount()

    // simula o recarregar: tudo e montado de novo, o endereco continua o mesmo
    render(<App inicial="/buscar?q=como%20orar%3F" />)

    expect(await screen.findByText('Resposta pronta.')).toBeInTheDocument()
    expect(buscasNaApi()).toHaveLength(1)
    expect(chamadas.filter((c) => c.caminho === '/api/resposta')).toHaveLength(1)
  })

  it('um endereco com outra pergunta busca de novo em vez de usar a conversa guardada', async () => {
    const primeira = render(<App inicial="/buscar?q=primeira" />)
    await screen.findByText('Resposta pronta.')
    primeira.unmount()

    render(<App inicial="/buscar?q=segunda" />)

    await waitFor(() => expect(buscasNaApi()).toHaveLength(2))
    expect(buscasNaApi()[1].corpo.pergunta).toBe('segunda')
  })

  it('conversa guardada corrompida e ignorada: comeca da tela inicial', async () => {
    sessionStorage.setItem('verbo-conversa', '{quebrado')
    render(<App />)

    expect(await screen.findByLabelText('Qual e a sua pergunta?')).toBeInTheDocument()
  })
})

describe('buscas recentes', () => {
  it('a busca feita aparece no historico e tocar nela busca de novo', async () => {
    const primeira = render(<App inicial="/buscar?q=como%20orar%3F" />)
    await screen.findByText('Resposta pronta.')
    expect(lerHistorico()).toEqual(['como orar?'])
    fireEvent.click(screen.getByRole('button', { name: 'Nova busca' }))
    await screen.findByLabelText('Qual e a sua pergunta?')

    fireEvent.click(await screen.findByRole('button', { name: 'como orar?' }))

    await waitFor(() => expect(buscasNaApi()).toHaveLength(2))
    expect(await screen.findByText('Resposta pronta.')).toBeInTheDocument()
    primeira.unmount()
  })

  it('Limpar historico apaga a lista e o que estava guardado', async () => {
    render(<App inicial="/buscar?q=como%20orar%3F" />)
    await screen.findByText('Resposta pronta.')
    fireEvent.click(screen.getByRole('button', { name: 'Nova busca' }))

    fireEvent.click(await screen.findByRole('button', { name: 'Limpar historico' }))

    expect(screen.queryByRole('region', { name: 'Buscas recentes' })).not.toBeInTheDocument()
    expect(lerHistorico()).toEqual([])
  })

  it('sem buscas anteriores nao mostra a secao', async () => {
    render(<App />)
    await screen.findByLabelText('Qual e a sua pergunta?')
    expect(screen.queryByRole('region', { name: 'Buscas recentes' })).not.toBeInTheDocument()
  })

  it('falha na busca nao entra no historico', async () => {
    vi.stubGlobal('fetch', vi.fn((caminho: string) =>
      caminho === '/api/versiculos'
        ? Promise.resolve(json({ detail: 'IA indisponivel' }, 503))
        : Promise.resolve(json([])),
    ))
    render(<App inicial="/buscar?q=falha" />)

    expect(await screen.findByRole('alert')).toHaveTextContent('IA indisponivel')
    expect(lerHistorico()).toEqual([])
  })
})

describe('copiar link da busca', () => {
  function simularAreaDeTransferencia(escrever: (texto: string) => Promise<void>) {
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: vi.fn(escrever) },
      configurable: true,
    })
    return (navigator.clipboard.writeText as ReturnType<typeof vi.fn>)
  }

  it('copia o endereco completo da busca e avisa', async () => {
    const escrever = simularAreaDeTransferencia(() => Promise.resolve())
    render(<App inicial="/buscar?q=como%20orar%3F" />)
    await screen.findByText('Resposta pronta.')

    fireEvent.click(screen.getByRole('button', { name: 'Copiar link da busca' }))

    await waitFor(() => expect(escrever).toHaveBeenCalledTimes(1))
    expect(escrever.mock.calls[0][0]).toBe(`${window.location.origin}/buscar?q=como%20orar%3F`)
    expect(await screen.findByRole('status')).toHaveTextContent('Link copiado.')
  })

  it('se o navegador nao deixar copiar, explica o que fazer', async () => {
    simularAreaDeTransferencia(() => Promise.reject(new Error('negado')))
    render(<App inicial="/buscar?q=como%20orar%3F" />)
    await screen.findByText('Resposta pronta.')

    fireEvent.click(screen.getByRole('button', { name: 'Copiar link da busca' }))

    expect(await screen.findByRole('status')).toHaveTextContent('Nao foi possivel copiar')
  })
})
