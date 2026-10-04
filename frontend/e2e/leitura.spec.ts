import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
import { simularApi } from './api-simulada.ts'

// Rodam em todos os projetos (computador e celulares) e, como o capitulo e pedido pela URL,
// tambem contra o site no ar (E2E_URL), so lendo.
test.beforeEach(async ({ page }) => {
  await simularApi(page)
})

const CAPITULO = '/ler/S%C3%A3o%20Lucas/11'
const rolar = (page: Page) => page.getByRole('button', { name: /rolar a pagina sozinha/i })
const parar = (page: Page) => page.getByRole('button', { name: /parar a rolagem automatica/i })
const scrollY = (page: Page) => page.evaluate(() => Math.round(window.scrollY))

async function abrirCapitulo(page: Page) {
  await page.goto(CAPITULO)
  await expect(page.getByRole('heading', { name: /São Lucas 11/ })).toBeVisible()
}

test.describe('modo leitura (rolagem automatica)', () => {
  test('o botao Rolar aparece no capitulo, dentro da tela, e nao na tela inicial', async ({ page }) => {
    await page.goto('/')
    await expect(rolar(page)).toHaveCount(0)

    await abrirCapitulo(page)

    await expect(rolar(page)).toBeVisible()
    const tela = page.viewportSize()!
    const caixa = (await rolar(page).boundingBox())!
    expect(caixa.x + caixa.width).toBeLessThanOrEqual(tela.width)
    expect(caixa.y + caixa.height).toBeLessThanOrEqual(tela.height)
  })

  test('ao ligar a pagina desce sozinha e o botao vira Parar', async ({ page }) => {
    await abrirCapitulo(page)
    expect(await scrollY(page)).toBe(0)

    await rolar(page).click()

    await expect(parar(page)).toBeVisible()
    await expect.poll(() => scrollY(page), { timeout: 6000 }).toBeGreaterThan(15)
  })

  test('Parar interrompe a rolagem e ela nao volta sozinha', async ({ page }) => {
    await abrirCapitulo(page)
    await rolar(page).click()
    await expect.poll(() => scrollY(page), { timeout: 6000 }).toBeGreaterThan(10)

    await parar(page).click()
    await expect(rolar(page)).toBeVisible()
    const parado = await scrollY(page)
    await page.waitForTimeout(700)

    expect(await scrollY(page)).toBe(parado)
  })

  test('a roda do mouse assume o controle e para a rolagem automatica', async ({ page }, testInfo) => {
    test.skip(testInfo.project.name.startsWith('celular'), 'roda do mouse e do computador')
    await abrirCapitulo(page)
    await rolar(page).click()
    await expect(parar(page)).toBeVisible()

    await page.mouse.move(600, 400)
    await page.mouse.wheel(0, 200)

    await expect(rolar(page)).toBeVisible()
  })

  test('tocar na tela assume o controle e para a rolagem (celular)', async ({ page }, testInfo) => {
    test.skip(!testInfo.project.name.startsWith('celular'), 'toque e do celular')
    await abrirCapitulo(page)
    await rolar(page).tap()
    await expect(parar(page)).toBeVisible()

    const tela = page.viewportSize()!
    await page.touchscreen.tap(Math.round(tela.width / 2), Math.round(tela.height / 3))

    await expect(rolar(page)).toBeVisible()
  })

  test('o botao tem tamanho confortavel para o dedo em tela de toque', async ({ page }, testInfo) => {
    test.skip(!testInfo.project.name.startsWith('celular'), 'alvo de toque so vale no celular')
    await abrirCapitulo(page)

    const caixa = (await rolar(page).boundingBox())!

    expect(caixa.width).toBeGreaterThanOrEqual(44)
    expect(caixa.height).toBeGreaterThanOrEqual(44)
  })

  test('trocar de capitulo desliga a rolagem e comeca no topo', async ({ page }) => {
    await abrirCapitulo(page)
    await rolar(page).click()
    await expect.poll(() => scrollY(page), { timeout: 6000 }).toBeGreaterThan(10)

    await page.getByRole('link', { name: 'Proximo capitulo' }).scrollIntoViewIfNeeded()
    await page.getByRole('link', { name: 'Proximo capitulo' }).click()

    await expect(page.getByRole('heading', { name: /São Lucas 12/ })).toBeVisible()
    await expect(rolar(page)).toBeVisible()
    await expect.poll(() => scrollY(page)).toBeLessThan(5)
  })
})

test.describe('navegacao entre capitulos', () => {
  test('mostra anterior e proximo no fim do texto, lado a lado', async ({ page }) => {
    await abrirCapitulo(page)

    const anterior = page.getByRole('link', { name: 'Capitulo anterior' })
    const proximo = page.getByRole('link', { name: 'Proximo capitulo' })
    await proximo.scrollIntoViewIfNeeded()

    await expect(anterior).toHaveAttribute('href', '/ler/S%C3%A3o%20Lucas/10')
    await expect(proximo).toHaveAttribute('href', '/ler/S%C3%A3o%20Lucas/12')
    const a = (await anterior.boundingBox())!
    const p = (await proximo.boundingBox())!
    expect(Math.abs(a.y - p.y)).toBeLessThan(4)
    expect(p.x).toBeGreaterThan(a.x + a.width - 1)
    const tela = page.viewportSize()!
    expect(p.x + p.width).toBeLessThanOrEqual(tela.width)
  })

  test('Proximo capitulo abre o seguinte e volta ao topo', async ({ page }) => {
    await abrirCapitulo(page)
    await page.getByRole('link', { name: 'Proximo capitulo' }).scrollIntoViewIfNeeded()
    expect(await scrollY(page)).toBeGreaterThan(100)

    await page.getByRole('link', { name: 'Proximo capitulo' }).click()

    await expect(page).toHaveURL(/\/ler\/S%C3%A3o%20Lucas\/12$/)
    await expect(page.getByRole('heading', { name: /São Lucas 12/ })).toBeVisible()
    await expect.poll(() => scrollY(page)).toBeLessThan(5)
  })

  test('Capitulo anterior abre o anterior', async ({ page }) => {
    await abrirCapitulo(page)
    await page.getByRole('link', { name: 'Capitulo anterior' }).scrollIntoViewIfNeeded()

    await page.getByRole('link', { name: 'Capitulo anterior' }).click()

    await expect(page.getByRole('heading', { name: /São Lucas 10/ })).toBeVisible()
  })
})

test.describe('tela inicial', () => {
  test('mostra o rodape com autoria e licenca', async ({ page }) => {
    await page.goto('/')

    const autor = page.getByRole('link', { name: 'Armando Netto' })
    await expect(autor).toBeVisible()
    await expect(autor).toHaveAttribute('href', 'https://armandonetto.com/')
    await expect(page.getByRole('link', { name: 'Licenca Verbo 1.0' })).toBeVisible()
  })

  test('o botao da barra mostra o que faz, com texto e borda visiveis', async ({ page }) => {
    await page.goto('/')

    const botao = page.getByRole('button', { name: /barra lateral/i })
    await expect(botao).toContainText(/Fechar barra|Abrir barra/)
    const largura = (await botao.boundingBox())!.width
    expect(largura).toBeGreaterThan(80)
    const borda = await botao.evaluate((el) => getComputedStyle(el).borderTopWidth)
    expect(parseFloat(borda)).toBeGreaterThan(0)
  })

  test('o texto do botao da barra acompanha o estado', async ({ page }) => {
    await page.goto('/')
    const botao = page.getByRole('button', { name: /barra lateral/i })
    const aberta = (await botao.getAttribute('aria-expanded')) === 'true'
    await expect(botao).toContainText(aberta ? 'Fechar barra' : 'Abrir barra')

    await botao.click()

    await expect(botao).toContainText(aberta ? 'Abrir barra' : 'Fechar barra')
  })

  test('o botao da barra e o de tema nao se sobrepoem nem saem da tela', async ({ page }) => {
    await page.goto('/')
    const tela = page.viewportSize()!

    const a = (await page.getByRole('button', { name: /barra lateral/i }).boundingBox())!
    const b = (await page.getByRole('button', { name: /tema/i }).boundingBox())!

    expect(a.x).toBeGreaterThanOrEqual(0)
    expect(b.x + b.width).toBeLessThanOrEqual(tela.width)
    expect(a.x + a.width).toBeLessThanOrEqual(b.x)
  })
})
