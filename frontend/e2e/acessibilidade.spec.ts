import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
import { contraSiteReal, simularApi } from './api-simulada.ts'

// Varredura de acessibilidade (axe-core, regras WCAG 2.0 e 2.1 niveis A e AA) nas telas principais,
// nos 4 tamanhos de tela do projeto. Ela acha o que da para medir sozinho: contraste, rotulos,
// nomes de botoes, papeis e ordem dos titulos. Nao substitui testar com leitor de tela.
test.beforeEach(async ({ page }) => {
  await simularApi(page)
})

async function varrer(page: Page) {
  const resultado = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze()
  // Mostra no erro o que falhou e onde, em vez de so "esperava 0"
  const resumo = resultado.violations.map((v) => ({
    regra: v.id,
    impacto: v.impact,
    ajuda: v.help,
    elementos: v.nodes.slice(0, 3).map((n) => `${n.target.join(' ')} -> ${n.any[0]?.message ?? n.failureSummary}`),
  }))
  expect(resumo, JSON.stringify(resumo, null, 2)).toEqual([])
}

// No celular a barra e uma gaveta fechada; no computador ja vem aberta
async function abrirBarra(page: Page) {
  const barra = page.getByRole('button', { name: /barra lateral/i })
  if ((await barra.getAttribute('aria-expanded')) === 'false') await barra.click()
}

async function buscar(page: Page) {
  await page.getByLabel('Qual e a sua pergunta?').fill('como orar?')
  await page.getByRole('button', { name: 'Buscar' }).click()
  await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
}

test('tela inicial', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Explore a Biblia' })).toBeVisible()

  await varrer(page)
})

test('leitura de um capitulo', async ({ page }) => {
  test.skip(contraSiteReal, 'depende dos dados simulados')
  await page.goto('/ler/S%C3%A3o%20Lucas/1')
  await expect(page.getByText('Versiculo 1 do capitulo')).toBeVisible()

  await varrer(page)
})

test('conversa depois de uma busca', async ({ page }) => {
  test.skip(contraSiteReal, 'depende dos dados simulados')
  await page.goto('/')
  await buscar(page)

  await varrer(page)
})

test('conversa com a barra de versiculos aberta', async ({ page }) => {
  test.skip(contraSiteReal, 'depende dos dados simulados')
  await page.goto('/')
  await buscar(page)
  const barra = page.getByRole('button', { name: /barra lateral/i })
  if ((await barra.getAttribute('aria-expanded')) === 'false') await barra.click()
  await expect(page.locator('#barra-lateral').getByRole('listitem').first()).toBeVisible()

  await varrer(page)
})

test('tela inicial com buscas recentes', async ({ page }) => {
  test.skip(contraSiteReal, 'depende dos dados simulados')
  await page.goto('/')
  await buscar(page)
  await abrirBarra(page)
  await page.getByRole('button', { name: 'Nova busca' }).click()
  await expect(page.getByLabel('Qual e a sua pergunta?')).toBeVisible()
  const barra = page.getByRole('button', { name: /barra lateral/i })
  if ((await barra.getAttribute('aria-expanded')) === 'false') await barra.click()
  await expect(page.getByRole('region', { name: 'Buscas recentes' })).toBeVisible()

  await varrer(page)
})

test.describe('tema escuro', () => {
  async function escurecer(page: Page) {
    await page.getByRole('button', { name: /tema/i }).click()
    await expect(page.locator('html')).toHaveAttribute('data-tema', 'escuro')
  }

  test('tela inicial', async ({ page }) => {
    await page.goto('/')
    await escurecer(page)

    await varrer(page)
  })

  test('conversa depois de uma busca', async ({ page }) => {
    test.skip(contraSiteReal, 'depende dos dados simulados')
    await page.goto('/')
    await escurecer(page)
    await buscar(page)

    await varrer(page)
  })
})
