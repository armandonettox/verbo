import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
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

function versiculo(i: number) {
  return {
    referencia: `Livro ${i}:1`,
    texto: `Texto do versiculo ${i}`,
    similaridade: 50 - i,
    livro: 'Livro',
    capitulo: i,
  }
}

const BUSCA = {
  pergunta: 'como orar?',
  modo: 'nvidia',
  aviso: null,
  versiculos: Array.from({ length: 6 }, (_, i) => versiculo(i + 1)),
}

type Rota = (corpo: Record<string, unknown>) => Response | Promise<Response>
let rotas: Record<string, Rota>
let chamadas: { caminho: string; corpo: Record<string, unknown> }[]

beforeEach(() => {
  chamadas = []
  rotas = {
    '/api/livros': () => json([]),
    '/api/versiculo-do-dia': () => json({ referencia: 'Gn 1,1', texto: 'x', data: '2026-10-03' }),
    '/api/versiculos': () => json(BUSCA),
    '/api/resposta': () => json({ resposta: 'Resposta **inicial**.' }),
  }
  vi.stubGlobal(
    'fetch',
    vi.fn((caminho: string, opcoes?: RequestInit) => {
      const corpo = opcoes?.body ? JSON.parse(opcoes.body as string) : {}
      chamadas.push({ caminho, corpo })
      const chave = Object.keys(rotas).find((r) => caminho.startsWith(r))
      if (!chave) return Promise.reject(new Error(`rota nao simulada: ${caminho}`))
      return Promise.resolve(rotas[chave](corpo))
    }),
  )
})

afterEach(() => vi.unstubAllGlobals())

async function abrirConversa() {
  render(
    <MemoryRouter>
      <BuscaProvider>
        <Home />
      </BuscaProvider>
    </MemoryRouter>,
  )
  fireEvent.change(screen.getByLabelText('Qual e a sua pergunta?'), { target: { value: 'como orar?' } })
  fireEvent.click(screen.getByRole('button', { name: 'Buscar' }))
  await screen.findByLabelText('Pergunta de acompanhamento')
}

function perguntarAcompanhamento(texto: string) {
  fireEvent.change(screen.getByLabelText('Pergunta de acompanhamento'), { target: { value: texto } })
  fireEvent.click(screen.getByRole('button', { name: 'Enviar' }))
}

describe('conversa', () => {
  it('renderiza o markdown da resposta e nao interpreta HTML cru', async () => {
    rotas['/api/resposta'] = () => json({ resposta: 'Texto **forte** <img src=x alt="perigo"> fim' })
    await abrirConversa()

    expect(screen.getByText('forte').tagName).toBe('STRONG')
    expect(screen.queryByAltText('perigo')).not.toBeInTheDocument()
  })

  it('mostra 4 versiculos e libera mais de 4 em 4', async () => {
    await abrirConversa()
    const lista = screen.getByRole('list')

    expect(within(lista).getAllByRole('listitem')).toHaveLength(4)

    fireEvent.click(screen.getByRole('button', { name: 'Mostrar mais resultados' }))

    expect(within(lista).getAllByRole('listitem')).toHaveLength(6)
    expect(screen.queryByRole('button', { name: 'Mostrar mais resultados' })).not.toBeInTheDocument()
  })

  it('Ver versiculo leva para a leitura do capitulo', async () => {
    await abrirConversa()

    const link = screen.getAllByRole('link', { name: 'Ver versiculo' })[0]

    expect(link).toHaveAttribute('href', '/ler/Livro/1')
  })

  it('pergunta de acompanhamento envia historico e original, e limpa o campo', async () => {
    rotas['/api/chat'] = () => json({ resposta: 'Segunda resposta.' })
    await abrirConversa()

    perguntarAcompanhamento('e depois?')

    expect(await screen.findByText('Segunda resposta.')).toBeInTheDocument()
    const { corpo } = chamadas.find((c) => c.caminho === '/api/chat')!
    expect(corpo.pergunta_original).toBe('como orar?')
    expect(corpo.resposta_original).toBe('Resposta **inicial**.')
    expect(corpo.historico).toEqual([])
    expect(corpo.pergunta_nova).toBe('e depois?')
    expect(screen.getByLabelText('Pergunta de acompanhamento')).toHaveValue('')
  })

  it('a segunda pergunta leva o primeiro turno no historico', async () => {
    rotas['/api/chat'] = () => json({ resposta: 'Outra resposta.' })
    await abrirConversa()
    perguntarAcompanhamento('primeira')
    await screen.findByText('Outra resposta.')

    perguntarAcompanhamento('segunda')
    await waitFor(() => expect(chamadas.filter((c) => c.caminho === '/api/chat')).toHaveLength(2))

    const { corpo } = chamadas.filter((c) => c.caminho === '/api/chat')[1]
    expect(corpo.historico).toEqual([
      { role: 'user', content: 'primeira' },
      { role: 'assistant', content: 'Outra resposta.' },
    ])
  })

  it('falha no acompanhamento mostra o erro, desfaz a pergunta e preserva o texto digitado', async () => {
    rotas['/api/chat'] = () => json({ detail: 'O servico de IA esta indisponivel.' }, 503)
    await abrirConversa()

    perguntarAcompanhamento('e depois?')

    expect(await screen.findByRole('alert')).toHaveTextContent('indisponivel')
    expect(screen.getByLabelText('Pergunta de acompanhamento')).toHaveValue('e depois?')
    expect(screen.queryByText('e depois?', { selector: 'p' })).not.toBeInTheDocument()
  })

  it('gerar novamente troca a resposta original e nao usa o cache do servidor', async () => {
    let pedidos = 0
    rotas['/api/resposta'] = () => json({ resposta: ++pedidos === 1 ? 'Resposta inicial.' : 'Resposta nova.' })
    await abrirConversa()

    fireEvent.click(screen.getByRole('button', { name: 'Gerar novamente' }))

    expect(await screen.findByText('Resposta nova.')).toBeInTheDocument()
    expect(screen.queryByText('Resposta inicial.')).not.toBeInTheDocument()
    const pedidosDeResposta = chamadas.filter((c) => c.caminho === '/api/resposta')
    expect(pedidosDeResposta.map((c) => c.corpo.usar_cache)).toEqual([true, false])
    expect(pedidosDeResposta[1].corpo.pergunta).toBe('como orar?')
  })

  it('mostra os versiculos antes de a resposta chegar', async () => {
    let liberar: (r: Response) => void = () => {}
    rotas['/api/resposta'] = () => new Promise<Response>((resolver) => (liberar = resolver))
    render(
      <MemoryRouter>
        <BuscaProvider>
          <Home />
        </BuscaProvider>
      </MemoryRouter>,
    )
    fireEvent.change(screen.getByLabelText('Qual e a sua pergunta?'), { target: { value: 'como orar?' } })
    fireEvent.click(screen.getByRole('button', { name: 'Buscar' }))

    // versiculos na barra e a pergunta na conversa, enquanto a resposta ainda esta sendo gerada
    expect(await screen.findAllByRole('listitem')).not.toHaveLength(0)
    expect(screen.getByText('como orar?', { selector: 'p' })).toBeInTheDocument()
    expect(screen.queryByText('inicial')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Gerar resposta' })).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Pergunta de acompanhamento')).not.toBeInTheDocument()

    liberar(json({ resposta: 'Resposta **inicial**.' }))

    expect(await screen.findByText('inicial')).toBeInTheDocument()
    expect(await screen.findByLabelText('Pergunta de acompanhamento')).toBeInTheDocument()
  })

  it('modo local nao oferece conversa, so os versiculos e o aviso', async () => {
    rotas['/api/versiculos'] = () => json({ ...BUSCA, modo: 'local', aviso: 'Mostrando uma busca simplificada.' })
    render(
      <MemoryRouter>
        <BuscaProvider>
          <Home />
        </BuscaProvider>
      </MemoryRouter>,
    )
    fireEvent.change(screen.getByLabelText('Qual e a sua pergunta?'), { target: { value: 'como orar?' } })
    fireEvent.click(screen.getByRole('button', { name: 'Buscar' }))

    expect(await screen.findByRole('status')).toHaveTextContent('busca simplificada')
    expect(screen.queryByLabelText('Pergunta de acompanhamento')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Gerar resposta' })).not.toBeInTheDocument()
    expect(screen.getAllByRole('listitem').length).toBeGreaterThan(0)
    expect(chamadas.some((c) => c.caminho === '/api/resposta')).toBe(false)
  })

  it('versiculos ok mas resposta falhou: mantem os versiculos e oferece gerar a resposta', async () => {
    let pedidos = 0
    rotas['/api/resposta'] = () =>
      ++pedidos === 1 ? json({ detail: 'A IA demorou demais para responder.' }, 503) : json({ resposta: 'Agora deu.' })
    render(
      <MemoryRouter>
        <BuscaProvider>
          <Home />
        </BuscaProvider>
      </MemoryRouter>,
    )
    fireEvent.change(screen.getByLabelText('Qual e a sua pergunta?'), { target: { value: 'como orar?' } })
    fireEvent.click(screen.getByRole('button', { name: 'Buscar' }))

    fireEvent.click(await screen.findByRole('button', { name: 'Gerar resposta' }))

    expect(await screen.findByText('Agora deu.')).toBeInTheDocument()
    expect(screen.getAllByRole('listitem').length).toBeGreaterThan(0)
    // a segunda tentativa ainda e a primeira resposta da busca, entao pode usar o cache
    const usos = chamadas.filter((c) => c.caminho === '/api/resposta').map((c) => c.corpo.usar_cache)
    expect(usos).toEqual([true, true])
  })
})
