import { defineConfig, devices } from '@playwright/test'

// Testes de ponta a ponta em navegador de verdade, com tela de computador e de celular
// (toque, largura e orientacao emulados).
//
// Por padrao sobem o build local (vite preview) com a API simulada pelos proprios testes.
// Para rodar contra o site no ar, so leitura: E2E_URL=https://verbo.armandonetto.com npm run e2e
const urlExterna = process.env.E2E_URL
const porta = 4173

export default defineConfig({
  testDir: './e2e',
  // A maquina de desenvolvimento costuma estar sobrecarregada; um por vez evita falso timeout
  workers: 1,
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  timeout: 30_000,
  expect: { timeout: 7_000 },
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : [['list']],
  use: {
    baseURL: urlExterna ?? `http://127.0.0.1:${porta}`,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'computador', use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } } },
    { name: 'celular', use: { ...devices['Pixel 7'] } },
    {
      name: 'celular-pequeno',
      use: { ...devices['Pixel 5'], viewport: { width: 360, height: 640 } },
    },
    {
      name: 'celular-paisagem',
      use: { ...devices['Pixel 7 landscape'] },
    },
  ],
  webServer: urlExterna
    ? undefined
    : {
        // O build precisa existir (npm run build); o script `npm run e2e` ja cuida disso
        command: `npm run preview -- --host 127.0.0.1 --port ${porta} --strictPort`,
        url: `http://127.0.0.1:${porta}`,
        reuseExistingServer: !process.env.CI,
        timeout: 60_000,
      },
})
