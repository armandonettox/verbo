import { expect, test } from '@playwright/test'
import { contraSiteReal, simularApi } from './api-simulada.ts'

// So no projeto "computador" (1280x800). Os de celular ficam em barra-lateral-celular.spec.ts
test.beforeEach(async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'computador', 'cenario de computador')
  await simularApi(page)
})

const botaoBarra = (page: import('@playwright/test').Page) =>
  page.getByRole('button', { name: /barra lateral/i })

test('a barra comeca aberta e mostra o seletor de livros', async ({ page }) => {
  await page.goto('/')

  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'true')
  await expect(botaoBarra(page)).toHaveAccessibleName('Fechar barra lateral')
  await expect(page.locator('#barra-lateral')).toBeVisible()
  await expect(page.getByRole('combobox', { name: 'Livro' })).toBeVisible()
})

test('fechar a barra libera a largura para o conteudo', async ({ page }) => {
  await page.goto('/')
  const conteudo = page.locator('.conteudo')
  const larguraAberta = (await conteudo.boundingBox())!.width

  await botaoBarra(page).click()

  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'false')
  await expect(page.locator('#barra-lateral')).toBeHidden()
  const larguraFechada = (await conteudo.boundingBox())!.width
  expect(larguraFechada).toBeGreaterThan(larguraAberta + 300)
})

test('a escolha fechada continua depois de recarregar e de abrir outra tela', async ({ page }) => {
  await page.goto('/')
  await botaoBarra(page).click()

  await page.reload()
  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'false')

  await page.goto('/ler/S%C3%A3o%20Lucas/11')
  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'false')
})

test('abrir de novo restaura a barra e grava a escolha', async ({ page }) => {
  await page.goto('/')
  await botaoBarra(page).click()
  await botaoBarra(page).click()

  await expect(page.locator('#barra-lateral')).toBeVisible()
  expect(await page.evaluate(() => localStorage.getItem('barra-lateral'))).toBe('aberta')
})

test('com a barra fechada o teclado nao entra nela', async ({ page }) => {
  await page.goto('/')
  await botaoBarra(page).click()

  // percorre os elementos focaveis e confirma que nenhum esta dentro da barra
  const dentroDaBarra: boolean[] = []
  for (let i = 0; i < 8; i++) {
    await page.keyboard.press('Tab')
    dentroDaBarra.push(await page.evaluate(() => !!document.activeElement?.closest('#barra-lateral')))
  }
  expect(dentroDaBarra.some(Boolean)).toBe(false)
})

test('o botao abre e fecha pelo teclado (Enter)', async ({ page }) => {
  await page.goto('/')
  await botaoBarra(page).focus()

  await page.keyboard.press('Enter')
  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'false')

  await page.keyboard.press('Enter')
  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'true')
})

test('Esc nao fecha a barra no computador', async ({ page }) => {
  await page.goto('/')

  await page.keyboard.press('Escape')

  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'true')
})

test('o ponto de corte e 800 px: acima fica fixa, ate 800 vira gaveta fechada', async ({ page }) => {
  await page.setViewportSize({ width: 801, height: 800 })
  await page.goto('/')
  await expect(page.locator('#barra-lateral')).toBeVisible()
  await expect(page.locator('.barra-fundo')).toHaveCount(0)

  await page.setViewportSize({ width: 800, height: 800 })
  await expect(botaoBarra(page)).toHaveAttribute('aria-expanded', 'false')
  await expect(page.locator('#barra-lateral')).toBeHidden()

  await page.setViewportSize({ width: 801, height: 800 })
  await expect(page.locator('#barra-lateral')).toBeVisible()
})

test.describe('com resultados de busca', () => {
  test.skip(contraSiteReal, 'depende dos dados simulados')

  test('a barra rola por conta propria e fica parada quando a pagina rola', async ({ page }) => {
    await page.goto('/')
    await page.getByLabel('Qual e a sua pergunta?').fill('como orar?')
    await page.getByRole('button', { name: 'Buscar' }).click()
    await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
    // 12 resultados: 4 visiveis mais dois cliques em "Mostrar mais" mostram todos
    for (let i = 0; i < 2; i++) await page.getByRole('button', { name: 'Mostrar mais resultados' }).click()

    const barra = page.locator('#barra-lateral')
    const rolaSozinha = await barra.evaluate((el) => el.scrollHeight > el.clientHeight)
    expect(rolaSozinha).toBe(true)

    await page.mouse.move(900, 400)
    await page.mouse.wheel(0, 600)
    const topoDaBarra = (await barra.boundingBox())!.y
    expect(topoDaBarra).toBe(0)
  })
})
