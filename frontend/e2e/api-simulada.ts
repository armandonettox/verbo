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

// 60 versiculos: o capitulo precisa ser mais alto que a tela para a rolagem automatica ter o que rolar
function capitulo(livro: string, numero: number) {
  return {
    livro,
    capitulo: numero,
    total_capitulos_livro: LIVROS.find((l) => l.livro === livro)?.total_capitulos ?? 1,
    versiculos: Array.from({ length: 60 }, (_, i) => ({
      versiculo: i + 1,
      texto: `Versiculo ${i + 1} do capitulo, com texto suficiente para ocupar uma linha inteira.`,
    })),
  }
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
    if (caminho.startsWith('/api/capitulos/')) {
      // /api/capitulos/{livro}/{numero}: devolve o capitulo pedido, nao sempre o mesmo
      const [, , , livro, numero] = decodeURIComponent(caminho).split('/')
      return rota.fulfill(json(capitulo(livro, Number(numero))))
    }
    // a busca e feita em duas etapas: primeiro os versiculos, depois a resposta
    if (caminho === '/api/versiculos') {
      return rota.fulfill(
        json({ pergunta: 'como orar?', modo: 'nvidia', aviso: null, versiculos: VERSICULOS }),
      )
    }
    if (caminho === '/api/resposta') {
      return rota.fulfill(json({ resposta: 'Jesus ensinou o Pai Nosso, citado em Lucas 11.' }))
    }
    return rota.fulfill({ status: 404, contentType: 'application/json', body: '{"detail":"nao simulado"}' })
  })
}
