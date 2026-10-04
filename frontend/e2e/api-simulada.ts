import type { Page } from '@playwright/test'

// A API simulada deixa os testes deterministicos e sem backend. Quando E2E_URL aponta para o
// site no ar, nada e simulado e os testes que dependem destes dados sao pulados.
export const contraSiteReal = Boolean(process.env.E2E_URL)

const LIVROS = [
  { livro: 'Genesis', indice_inicial: 0, total_capitulos: 50 },
  { livro: 'São Lucas', indice_inicial: 50, total_capitulos: 24 },
]

export const VERSICULOS = Array.from({ length: 12 }, (_, i) => ({
  referencia: `São Lucas ${i + 1}:1-12`,
  texto: `Texto do versiculo numero ${i + 1}. `.repeat(8),
  similaridade: 60 - i,
  livro: 'São Lucas',
  capitulo: i + 1,
}))

const CAPITULO = {
  livro: 'São Lucas',
  capitulo: 11,
  total_capitulos_livro: 24,
  versiculos: Array.from({ length: 30 }, (_, i) => ({
    versiculo: i + 1,
    texto: `Versiculo ${i + 1} do capitulo, com texto suficiente para ocupar uma linha inteira.`,
  })),
}

function json(corpo: unknown) {
  return { status: 200, contentType: 'application/json', body: JSON.stringify(corpo) }
}

export async function simularApi(page: Page) {
  if (contraSiteReal) return
  await page.route('**/api/**', async (rota) => {
    const url = new URL(rota.request().url())
    const caminho = url.pathname

    if (caminho === '/api/livros') return rota.fulfill(json(LIVROS))
    if (caminho === '/api/versiculo-do-dia') {
      return rota.fulfill(
        json({ referencia: 'Gênesis 1,1', texto: 'No principio Deus criou o ceu e a terra.', data: '2026-10-04' }),
      )
    }
    if (caminho.startsWith('/api/capitulos/')) return rota.fulfill(json(CAPITULO))
    if (caminho === '/api/buscar') {
      return rota.fulfill(
        json({
          pergunta: 'como orar?',
          modo: 'nvidia',
          resposta: 'Jesus ensinou o Pai Nosso, citado em Lucas 11.',
          aviso: null,
          versiculos: VERSICULOS,
        }),
      )
    }
    return rota.fulfill({ status: 404, contentType: 'application/json', body: '{"detail":"nao simulado"}' })
  })
}
