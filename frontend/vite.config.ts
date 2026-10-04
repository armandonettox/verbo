import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Em desenvolvimento a API roda no Docker (porta 8010). Em producao o nginx faz esse papel.
    proxy: {
      '/api': 'http://127.0.0.1:8010',
    },
  },
  test: {
    // jsdom simula o navegador pros testes de componentes React
    environment: 'jsdom',
    include: ['src/**/*.test.{ts,tsx}'],
    // Desmonta os componentes de cada teste (ver src/test-setup.ts)
    setupFiles: ['src/test-setup.ts'],
    // Restaura mocks e limpa a DOM entre testes, pra um teste nao vazar estado pro outro
    restoreMocks: true,
    clearMocks: true,
  },
})
