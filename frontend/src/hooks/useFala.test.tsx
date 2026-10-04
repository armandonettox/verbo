import { act, cleanup, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useFala } from './useFala.ts'

let ultimaFala: { text: string; lang: string; rate: number; onend?: () => void } | null = null

beforeEach(() => {
  ultimaFala = null
  vi.stubGlobal(
    'SpeechSynthesisUtterance',
    class {
      text: string
      lang = ''
      rate = 1
      onend?: () => void
      onerror?: () => void
      constructor(texto: string) {
        this.text = texto
        // eslint-disable-next-line @typescript-eslint/no-this-alias
        ultimaFala = this
      }
    },
  )
  vi.stubGlobal('speechSynthesis', { speak: vi.fn(), cancel: vi.fn() })
})

afterEach(() => {
  // desmonta antes de remover o speechSynthesis falso, que o hook usa ao desmontar
  cleanup()
  vi.unstubAllGlobals()
})

describe('useFala', () => {
  it('fala o texto em pt-BR com a velocidade padrao', () => {
    const { result } = renderHook(() => useFala())

    act(() => result.current.falar('No principio era o Verbo'))

    expect(result.current.falando).toBe(true)
    expect(ultimaFala?.text).toBe('No principio era o Verbo')
    expect(ultimaFala?.lang).toBe('pt-BR')
    expect(ultimaFala?.rate).toBe(0.95)
    expect(window.speechSynthesis.speak).toHaveBeenCalledTimes(1)
  })

  it('volta a nao falando quando a fala termina', () => {
    const { result } = renderHook(() => useFala())
    act(() => result.current.falar('texto'))

    act(() => ultimaFala?.onend?.())

    expect(result.current.falando).toBe(false)
  })

  it('parar cancela a fala', () => {
    const { result } = renderHook(() => useFala())
    act(() => result.current.falar('texto'))

    act(() => result.current.parar())

    expect(result.current.falando).toBe(false)
    expect(window.speechSynthesis.cancel).toHaveBeenCalled()
  })

  it('cancela a fala ao desmontar se ele a iniciou', () => {
    const { result, unmount } = renderHook(() => useFala())
    act(() => result.current.falar('texto'))
    vi.mocked(window.speechSynthesis.cancel).mockClear()

    unmount()

    expect(window.speechSynthesis.cancel).toHaveBeenCalledTimes(1)
  })

  it('nao cancela ao desmontar se nunca falou (nao interrompe outro botao)', () => {
    const { unmount } = renderHook(() => useFala())

    unmount()

    expect(window.speechSynthesis.cancel).not.toHaveBeenCalled()
  })

  it('sem suporte do navegador, nao quebra e informa', () => {
    vi.unstubAllGlobals()
    // jsdom nao tem speechSynthesis
    const { result } = renderHook(() => useFala())

    expect(result.current.suportado).toBe(false)
    expect(() => act(() => result.current.falar('texto'))).not.toThrow()
  })
})
