import { expect, test } from '@playwright/test'
import type { Locator, Page } from '@playwright/test'
import { contraSiteReal, simularApi } from './api-simulada.ts'

// O teclado virtual do celular tira boa parte da altura da tela. Aqui ele e simulado encolhendo a
// janela (como o Chrome do Android faz com interactive-widget=resizes-content) e conferimos que o
// campo que a pessoa esta digitando e o botao de enviar continuam visiveis e sem nada por cima.
test.beforeEach(async ({ page }, testInfo) => {
  test.skip(!testInfo.project.name.startsWith('celular'), 'cenario de celular')
  await simularApi(page)
})

// Fracao da altura que sobra com o teclado aberto: em pe ele ocupa uns 45% da tela, e na horizontal
// quase tudo
function alturaComTeclado(page: Page) {
  const tela = page.viewportSize()!
  const fracao = tela.width > tela.height ? 0.5 : 0.55
  return Math.round(tela.height * fracao)
}

async function abrirTeclado(page: Page) {
  const tela = page.viewportSize()!
  await page.setViewportSize({ width: tela.width, height: alturaComTeclado(page) })
}

// O que esta no ponto central do elemento e o proprio elemento (ou algo dentro dele)? Se um botao
// fixo ou o fundo da gaveta estiver por cima, a resposta e nao.
async function estaLivre(elemento: Locator) {
  return elemento.evaluate((el) => {
    const caixa = el.getBoundingClientRect()
    const topo = document.elementFromPoint(caixa.left + caixa.width / 2, caixa.top + caixa.height / 2)
    return topo !== null && el.contains(topo)
  })
}

async function semRolagemHorizontal(page: Page) {
  const sobra = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )
  expect(sobra).toBeLessThanOrEqual(0)
}

test('tela inicial: o campo de busca e o botao Buscar ficam visiveis com o teclado aberto', async ({ page }) => {
  await page.goto('/')
  const campo = page.getByLabel('Qual e a sua pergunta?')
  await campo.tap()
  await abrirTeclado(page)
  await campo.scrollIntoViewIfNeeded()

  await expect(campo).toBeInViewport({ ratio: 1 })
  await expect(page.getByRole('button', { name: 'Buscar' })).toBeInViewport({ ratio: 1 })
  expect(await estaLivre(campo)).toBe(true)
  expect(await estaLivre(page.getByRole('button', { name: 'Buscar' }))).toBe(true)
  await semRolagemHorizontal(page)
})

test('tela inicial: digitar com o teclado aberto e buscar funciona', async ({ page }) => {
  test.skip(contraSiteReal, 'depende dos dados simulados')
  await page.goto('/')
  const campo = page.getByLabel('Qual e a sua pergunta?')
  await campo.tap()
  await abrirTeclado(page)
  await campo.fill('como orar?')

  await page.getByRole('button', { name: 'Buscar' }).tap()

  await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
})

test.describe('depois de uma busca', () => {
  test.skip(contraSiteReal, 'depende dos dados simulados')

  test('o campo de acompanhamento fica visivel e livre com o teclado aberto', async ({ page }) => {
    await page.goto('/')
    await page.getByLabel('Qual e a sua pergunta?').fill('como orar?')
    await page.getByRole('button', { name: 'Buscar' }).tap()
    await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
    const campo = page.getByLabel('Pergunta de acompanhamento')
    await campo.tap()
    await abrirTeclado(page)

    await expect(campo).toBeInViewport({ ratio: 1 })
    await expect(page.getByRole('button', { name: 'Enviar' })).toBeInViewport({ ratio: 1 })
    expect(await estaLivre(campo)).toBe(true)
    expect(await estaLivre(page.getByRole('button', { name: 'Enviar' }))).toBe(true)
    await semRolagemHorizontal(page)
  })

  test('o texto digitado aparece inteiro no campo com o teclado aberto', async ({ page }) => {
    await page.goto('/')
    await page.getByLabel('Qual e a sua pergunta?').fill('como orar?')
    await page.getByRole('button', { name: 'Buscar' }).tap()
    await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
    const campo = page.getByLabel('Pergunta de acompanhamento')
    await campo.tap()
    await abrirTeclado(page)

    await campo.fill('e se eu errar a oracao?')

    await expect(campo).toHaveValue('e se eu errar a oracao?')
    await expect(campo).toBeInViewport({ ratio: 1 })
  })
})
