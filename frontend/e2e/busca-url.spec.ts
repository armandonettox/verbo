import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
import { contraSiteReal, simularApi } from './api-simulada.ts'

// Endereco da busca (/buscar?q=...), conversa que sobrevive a recarregar, buscas recentes e o botao
// de copiar o link. Usam a API simulada, entao nao rodam contra o site no ar.
test.skip(contraSiteReal, 'depende dos dados simulados')

test.beforeEach(async ({ page }) => {
  await simularApi(page)
})

const ENDERECO = '/buscar?q=como%20orar%3F'

// No celular a barra e uma gaveta fechada; no computador ja vem aberta
async function abrirBarra(page: Page) {
  const barra = page.getByRole('button', { name: /barra lateral/i })
  if ((await barra.getAttribute('aria-expanded')) === 'false') await barra.click()
}

function contarBuscas(page: Page) {
  const contagem = { versiculos: 0, respostas: 0 }
  page.on('request', (pedido) => {
    const caminho = new URL(pedido.url()).pathname
    if (caminho === '/api/versiculos') contagem.versiculos++
    if (caminho === '/api/resposta') contagem.respostas++
  })
  return contagem
}

test('abrir o link da busca faz a busca e mostra a resposta', async ({ page }) => {
  const buscas = contarBuscas(page)
  await page.goto(ENDERECO)

  await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
  await expect(page.getByText('como orar?', { exact: true })).toBeVisible()
  expect(buscas.versiculos).toBe(1)
})

test('buscar pelo campo coloca a pergunta no endereco', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('Qual e a sua pergunta?').fill('como orar?')
  await page.getByRole('button', { name: 'Buscar' }).click()

  await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
  await expect(page).toHaveURL(/\/buscar\?q=como%20orar%3F$/)
})

test('recarregar a pagina traz a conversa de volta sem buscar de novo', async ({ page }) => {
  const buscas = contarBuscas(page)
  await page.goto(ENDERECO)
  await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()

  await page.reload()

  await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
  await expect(page.getByLabel('Pergunta de acompanhamento')).toBeVisible()
  expect(buscas.versiculos).toBe(1)
  expect(buscas.respostas).toBe(1)
})

test('o link aberto numa aba nova (sem conversa guardada) faz a busca', async ({ page }) => {
  await page.goto(ENDERECO)
  await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()

  const outra = await page.context().newPage()
  await simularApi(outra)
  const buscas = contarBuscas(outra)
  await outra.goto(ENDERECO)

  await expect(outra.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
  expect(buscas.versiculos).toBe(1)
})

test('/buscar sem pergunta volta para a tela inicial', async ({ page }) => {
  await page.goto('/buscar')

  await expect(page.getByLabel('Qual e a sua pergunta?')).toBeVisible()
  await expect(page).toHaveURL(/\/$/)
})

test('Copiar link da busca copia o endereco que reabre a mesma busca', async ({ page }) => {
  await page.context().grantPermissions(['clipboard-read', 'clipboard-write'])
  await page.goto(ENDERECO)
  await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
  await abrirBarra(page)

  await page.getByRole('button', { name: 'Copiar link da busca' }).click()

  await expect(page.getByRole('status')).toHaveText('Link copiado.')
  const copiado = await page.evaluate(() => navigator.clipboard.readText())
  expect(copiado).toBe(new URL(ENDERECO, page.url()).href)
})

test('a busca aparece nas buscas recentes e tocar nela busca de novo', async ({ page }) => {
  const buscas = contarBuscas(page)
  await page.goto(ENDERECO)
  await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
  await abrirBarra(page)
  await page.getByRole('button', { name: 'Nova busca' }).click()
  await expect(page.getByLabel('Qual e a sua pergunta?')).toBeVisible()
  await abrirBarra(page)

  await page.getByRole('region', { name: 'Buscas recentes' }).getByRole('button', { name: 'como orar?' }).click()

  await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
  expect(buscas.versiculos).toBe(2)
})

test('Limpar historico esvazia as buscas recentes e continua assim depois de recarregar', async ({ page }) => {
  await page.goto(ENDERECO)
  await expect(page.getByText('Jesus ensinou o Pai Nosso')).toBeVisible()
  await abrirBarra(page)
  await page.getByRole('button', { name: 'Nova busca' }).click()
  await abrirBarra(page)

  await page.getByRole('button', { name: 'Limpar historico' }).click()
  await expect(page.getByRole('region', { name: 'Buscas recentes' })).toHaveCount(0)

  await page.reload()
  await abrirBarra(page)
  await expect(page.getByRole('region', { name: 'Buscas recentes' })).toHaveCount(0)
})
