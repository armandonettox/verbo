import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { BotaoRolagem } from './BotaoRolagem.tsx'

// Simula a geometria da pagina (o jsdom nao tem layout): altura total, altura visivel e posicao
function simularPagina({ total, visivel, topo }: { total: number; visivel: number; topo: number }) {
  const el = document.documentElement
  Object.defineProperty(el, 'scrollHeight', { value: total, configurable: true })
  Object.defineProperty(el, 'clientHeight', { value: visivel, configurable: true })
  Object.defineProperty(el, 'scrollTop', { value: topo, configurable: true, writable: true })
}

beforeEach(() => {
  vi.useFakeTimers()
})

afterEach(() => {
  cleanup()
  vi.useRealTimers()
  for (const prop of ['scrollHeight', 'clientHeight', 'scrollTop']) {
    delete (document.documentElement as unknown as Record<string, unknown>)[prop]
  }
})

describe('BotaoRolagem (modo leitura)', () => {
  it('nao aparece quando a pagina cabe na tela', () => {
    simularPagina({ total: 600, visivel: 600, topo: 0 })

    render(<BotaoRolagem />)

    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('aparece como Rolar quando ha o que rolar', () => {
    simularPagina({ total: 3000, visivel: 600, topo: 0 })

    render(<BotaoRolagem />)

    const botao = screen.getByRole('button', { name: /rolar a pagina sozinha/i })
    expect(botao).toHaveTextContent('Rolar')
    expect(botao).toHaveAttribute('aria-pressed', 'false')
  })

  it('ao ligar vira Parar e rola 1 px a cada 40 ms', () => {
    simularPagina({ total: 3000, visivel: 600, topo: 0 })
    render(<BotaoRolagem />)

    fireEvent.click(screen.getByRole('button'))
    act(() => vi.advanceTimersByTime(400))

    expect(screen.getByRole('button')).toHaveTextContent('Parar')
    expect(screen.getByRole('button')).toHaveAttribute('aria-pressed', 'true')
    expect(window.scrollBy).toHaveBeenCalledTimes(10)
    expect(window.scrollBy).toHaveBeenCalledWith(0, 1)
  })

  it('clicar de novo para a rolagem', () => {
    simularPagina({ total: 3000, visivel: 600, topo: 0 })
    render(<BotaoRolagem />)
    fireEvent.click(screen.getByRole('button'))
    act(() => vi.advanceTimersByTime(200))

    fireEvent.click(screen.getByRole('button'))
    const chamadas = vi.mocked(window.scrollBy).mock.calls.length
    act(() => vi.advanceTimersByTime(1000))

    expect(screen.getByRole('button')).toHaveTextContent('Rolar')
    expect(window.scrollBy).toHaveBeenCalledTimes(chamadas)
  })

  it('para sozinha ao chegar no fim da pagina', () => {
    simularPagina({ total: 3000, visivel: 600, topo: 2399 })
    render(<BotaoRolagem />)
    fireEvent.click(screen.getByRole('button'))

    // o proximo passo coloca a pagina no fim (topo + visivel >= total - 2)
    ;(document.documentElement as unknown as { scrollTop: number }).scrollTop = 2400
    act(() => vi.advanceTimersByTime(80))

    expect(screen.getByRole('button')).toHaveTextContent('Rolar')
  })

  it.each([
    ['a roda do mouse', () => fireEvent.wheel(window)],
    ['o toque na tela', () => fireEvent.touchStart(window)],
    ['a seta para baixo', () => fireEvent.keyDown(window, { key: 'ArrowDown' })],
    ['a barra de espaco', () => fireEvent.keyDown(window, { key: ' ' })],
    ['Page Down', () => fireEvent.keyDown(window, { key: 'PageDown' })],
  ])('para quando a pessoa assume o controle com %s', (_, acao) => {
    simularPagina({ total: 3000, visivel: 600, topo: 0 })
    render(<BotaoRolagem />)
    fireEvent.click(screen.getByRole('button'))

    act(() => {
      acao()
    })

    expect(screen.getByRole('button')).toHaveTextContent('Rolar')
  })

  it('outras teclas nao interrompem', () => {
    simularPagina({ total: 3000, visivel: 600, topo: 0 })
    render(<BotaoRolagem />)
    fireEvent.click(screen.getByRole('button'))

    act(() => {
      fireEvent.keyDown(window, { key: 'a' })
    })

    expect(screen.getByRole('button')).toHaveTextContent('Parar')
  })

  it('tocar no proprio botao para desligar nao religa (o toque nao conta como assumir o controle)', () => {
    simularPagina({ total: 3000, visivel: 600, topo: 0 })
    render(<BotaoRolagem />)
    const botao = screen.getByRole('button')
    fireEvent.click(botao)

    // sequencia real de um toque: touchstart no botao e depois o clique
    act(() => {
      fireEvent.touchStart(botao)
    })
    expect(screen.getByRole('button')).toHaveTextContent('Parar')
    fireEvent.click(botao)

    expect(screen.getByRole('button')).toHaveTextContent('Rolar')
    act(() => vi.advanceTimersByTime(500))
    expect(screen.getByRole('button')).toHaveTextContent('Rolar')
  })

  it('some e para se a pagina deixar de ser rolavel (ex: tela maior)', () => {
    simularPagina({ total: 3000, visivel: 600, topo: 0 })
    render(<BotaoRolagem />)
    fireEvent.click(screen.getByRole('button'))

    simularPagina({ total: 500, visivel: 600, topo: 0 })
    act(() => {
      fireEvent(window, new Event('resize'))
    })

    expect(screen.queryByRole('button')).not.toBeInTheDocument()
    const chamadas = vi.mocked(window.scrollBy).mock.calls.length
    act(() => vi.advanceTimersByTime(500))
    expect(window.scrollBy).toHaveBeenCalledTimes(chamadas)
  })

  it('ao desmontar com a rolagem ligada nada continua rolando', () => {
    simularPagina({ total: 3000, visivel: 600, topo: 0 })
    const { unmount } = render(<BotaoRolagem />)
    fireEvent.click(screen.getByRole('button'))
    act(() => vi.advanceTimersByTime(80))
    const chamadas = vi.mocked(window.scrollBy).mock.calls.length

    unmount()
    act(() => vi.advanceTimersByTime(1000))

    expect(window.scrollBy).toHaveBeenCalledTimes(chamadas)
  })
})
