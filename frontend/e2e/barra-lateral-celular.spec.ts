import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
import { contraSiteReal, simularApi } from './api-simulada.ts'

// Projetos de celular: Pixel 7, Pixel 5 pequeno (360x640) e Pixel 7 em paisagem. Toque real.
test.beforeEach(async ({ page }, testInfo) => {
  test.skip(!testInfo.project.name.startsWith('celular'), 'cenario de celular')
  await simularApi(page)
})

const botaoBarra = (page: Page) => page.getByRole('button', { name: /barra lateral/i })
const botaoTema = (page: Page) => page.getByRole('button', { name: /tema/i })
const gaveta = (page: Page) => page.locator('#barra-lateral')

async function buscar(page: Page) {
  await page.getByLabel('Qual e a sua pergunta?').fill('como orar?')
  await page.getByRole('button', { name: 'Buscar' }).tap()
  await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
}

test('comeca com a gaveta fechada e sem rolagem horizontal', async ({ page }) => {
  await page.goto('/')

  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'false')
  await expect(gaveta(page)).toBeHidden()
  const sobra = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )
  expect(sobra).toBeLessThanOrEqual(0)
})

test('o botao da barra tem tamanho confortavel para o dedo (44 px)', async ({ page }) => {
  await page.goto('/')

  const caixa = (await botaoBarra(page).boundingBox())!

  expect(caixa.width).toBeGreaterThanOrEqual(44)
  expect(caixa.height).toBeGreaterThanOrEqual(44)
})

test('os botoes de barra e de tema ficam na tela e nao se sobrepoem', async ({ page }) => {
  await page.goto('/')
  const tela = page.viewportSize()!

  const a = (await botaoBarra(page).boundingBox())!
  const b = (await botaoTema(page).boundingBox())!

  for (const caixa of [a, b]) {
    expect(caixa.x).toBeGreaterThanOrEqual(0)
    expect(caixa.y).toBeGreaterThanOrEqual(0)
    expect(caixa.x + caixa.width).toBeLessThanOrEqual(tela.width)
  }
  const sobrepoe = a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height
  expect(sobrepoe).toBe(false)
})

test('tocar no botao abre a gaveta por cima do conteudo, com fundo escuro', async ({ page }) => {
  await page.goto('/')

  await botaoBarra(page).tap()

  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'true')
  await expect(gaveta(page)).toBeVisible()
  await expect(page.locator('.barra-fundo')).toBeVisible()
  const tela = page.viewportSize()!
  // a gaveta desliza em 0,2 s: espera chegar ao lugar antes de medir
  await expect
    .poll(async () => (await gaveta(page).boundingBox())!.x, { message: 'a gaveta termina a animacao' })
    .toBeGreaterThanOrEqual(0)
  const caixa = (await gaveta(page).boundingBox())!
  expect(caixa.width).toBeLessThanOrEqual(tela.width * 0.88 + 1)
  expect(caixa.width).toBeLessThanOrEqual(381)
  // deixa uma faixa do fundo visivel para tocar e fechar
  expect(caixa.x + caixa.width).toBeLessThan(tela.width)
})

test('tocar no fundo escuro fecha a gaveta', async ({ page }) => {
  await page.goto('/')
  await botaoBarra(page).tap()
  const tela = page.viewportSize()!

  await page.touchscreen.tap(tela.width - 6, Math.round(tela.height / 2))

  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'false')
  await expect(gaveta(page)).toBeHidden()
  await expect(page.locator('.barra-fundo')).toHaveCount(0)
})

test('Esc fecha a gaveta', async ({ page }) => {
  await page.goto('/')
  await botaoBarra(page).tap()

  await page.keyboard.press('Escape')

  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'false')
})

test('o botao continua tocavel com a gaveta aberta e fecha ao tocar de novo', async ({ page }) => {
  await page.goto('/')
  await botaoBarra(page).tap()
  await expect(gaveta(page)).toBeVisible()

  await botaoBarra(page).tap()

  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'false')
})

test('a escolha do celular nao e gravada (nao muda o computador)', async ({ page }) => {
  await page.goto('/')
  await botaoBarra(page).tap()
  await botaoBarra(page).tap()

  expect(await page.evaluate(() => localStorage.getItem('barra-lateral'))).toBeNull()
})

test('da para escolher livro e capitulo na gaveta e comecar a leitura', async ({ page }) => {
  test.skip(contraSiteReal, 'a leitura de capitulo usa dados simulados')
  await page.goto('/')
  await botaoBarra(page).tap()

  await page.getByRole('combobox', { name: 'Livro' }).selectOption('São Lucas')
  // em paisagem a gaveta e baixa: o botao precisa ser alcancavel rolando a propria gaveta
  await page.getByRole('button', { name: 'Comecar leitura' }).tap()

  await expect(page).toHaveURL(/\/ler\/S%C3%A3o%20Lucas\/1$/)
  await expect(page.getByRole('heading', { name: /São Lucas 1$/ })).toBeVisible()
  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'false')
})

test.describe('depois de uma busca', () => {
  test.skip(contraSiteReal, 'depende dos dados simulados')

  test('a resposta aparece primeiro, sem rolagem horizontal, e a gaveta fica fechada', async ({ page }) => {
    await page.goto('/')
    await buscar(page)

    await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'false')
    await expect(page.getByLabel('Pergunta de acompanhamento')).toBeVisible()
    const sobra = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(sobra).toBeLessThanOrEqual(0)
  })

  test('o aviso de citacoes fora dos versiculos aparece sem criar rolagem horizontal', async ({ page }) => {
    await page.route('**/api/resposta', (rota) =>
      rota.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          resposta: 'Jesus ensinou o Pai Nosso, citado em Lucas 11. Veja tambem Mateus 7.',
          citacoes_nao_confirmadas: ['São Mateus 7', 'Atos dos Apóstolos 26', 'II Coríntios 12'],
        }),
      }),
    )
    await page.goto('/')
    await page.getByLabel('Qual e a sua pergunta?').fill('como orar?')
    await page.getByRole('button', { name: 'Buscar' }).tap()

    const aviso = page.getByRole('note')
    await expect(aviso).toContainText('nao estavam entre os versiculos encontrados')
    await expect(aviso.getByRole('link', { name: 'São Mateus 7' })).toBeVisible()
    const sobra = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(sobra).toBeLessThanOrEqual(0)

    await aviso.getByRole('link', { name: 'São Mateus 7' }).tap()
    await expect(page).toHaveURL(/\/ler\/S%C3%A3o%20Mateus\/7$/)
  })

  test('o botao Ver versiculos na conversa abre a gaveta com os resultados', async ({ page }) => {
    await page.goto('/')
    await buscar(page)

    const ver = page.getByRole('button', { name: 'Ver versiculos (12)' })
    await expect(ver).toBeVisible()
    await ver.tap()

    await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'true')
    await expect(gaveta(page).getByRole('listitem')).toHaveCount(4)
    // com a gaveta aberta o atalho some
    await expect(ver).toBeHidden()
  })

  test('os versiculos ficam disponiveis enquanto a resposta ainda esta sendo gerada', async ({ page }) => {
    let liberar!: () => void
    const portao = new Promise<void>((resolver) => (liberar = resolver))
    await page.route('**/api/resposta', async (rota) => {
      await portao
      await rota.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ resposta: 'Jesus ensinou o Pai Nosso, citado em Lucas 11.' }),
      })
    })
    await page.goto('/')
    await page.getByLabel('Qual e a sua pergunta?').fill('como orar?')
    await page.getByRole('button', { name: 'Buscar' }).tap()

    await page.getByRole('button', { name: 'Ver versiculos (12)' }).tap()
    await expect(gaveta(page).getByRole('listitem')).toHaveCount(4)
    await expect(page.getByText('Jesus ensinou o Pai Nosso')).toHaveCount(0)

    liberar()
    await page.keyboard.press('Escape')
    await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
  })

  test('a gaveta mostra os versiculos e o Mostrar mais libera outros 4', async ({ page }) => {
    await page.goto('/')
    await buscar(page)
    await botaoBarra(page).tap()

    await expect(gaveta(page).getByRole('listitem')).toHaveCount(4)
    await gaveta(page).getByRole('button', { name: 'Mostrar mais resultados' }).tap()
    await expect(gaveta(page).getByRole('listitem')).toHaveCount(8)
  })

  test('rolar a gaveta ate o fim nao rola a pagina de tras', async ({ page }) => {
    await page.goto('/')
    await buscar(page)
    await botaoBarra(page).tap()
    for (let i = 0; i < 2; i++) await gaveta(page).getByRole('button', { name: 'Mostrar mais resultados' }).tap()
    const caixa = (await gaveta(page).boundingBox())!
    await page.mouse.move(caixa.x + caixa.width / 2, caixa.y + caixa.height / 2)

    // rola bem alem do fim da gaveta: o excesso nao pode passar para a pagina
    for (let i = 0; i < 6; i++) await page.mouse.wheel(0, 800)

    const rolagemDaPagina = await page.evaluate(() => window.scrollY)
    expect(rolagemDaPagina).toBe(0)
    const noFim = await gaveta(page).evaluate((el) => el.scrollTop + el.clientHeight >= el.scrollHeight - 2)
    expect(noFim).toBe(true)
  })

  test('com a gaveta aberta, rolar sobre o fundo escuro tambem nao rola a pagina', async ({ page }) => {
    await page.goto('/')
    await buscar(page)
    await botaoBarra(page).tap()
    const tela = page.viewportSize()!

    await page.mouse.move(tela.width - 6, Math.round(tela.height / 2))
    for (let i = 0; i < 4; i++) await page.mouse.wheel(0, 800)

    expect(await page.evaluate(() => window.scrollY)).toBe(0)
    // e a rolagem da pagina volta ao normal quando a gaveta fecha
    await page.keyboard.press('Escape')
    expect(await page.evaluate(() => getComputedStyle(document.body).overflow)).not.toBe('hidden')
  })

  test('Ver versiculo leva ao capitulo e a gaveta nao fica aberta na tela nova', async ({ page }) => {
    await page.goto('/')
    await buscar(page)
    await botaoBarra(page).tap()

    await gaveta(page).getByRole('link', { name: 'Ver versiculo' }).first().tap()

    await expect(page).toHaveURL(/\/ler\/S%C3%A3o%20Lucas\/1$/)
    await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'false')
    await expect(page.getByText('Versiculo 1 do capitulo')).toBeVisible()
  })
})
