import { act, cleanup, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { formatarTempo, useFalaProgresso } from './useFalaProgresso.ts'

let ultimaFala: { text: string; onend?: () => void } | null = null
const sintese = { speak: vi.fn(), cancel: vi.fn(), pause: vi.fn(), resume: vi.fn() }

beforeEach(() => {
  vi.useFakeTimers()
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
  vi.stubGlobal('speechSynthesis', sintese)
})

afterEach(() => {
  cleanup()
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

const TEXTO = Array.from({ length: 147 }, () => 'palavra').join(' ')

describe('formatarTempo', () => {
  it('formata minutos e segundos', () => {
    expect(formatarTempo(0)).toBe('0:00')
    expect(formatarTempo(65)).toBe('1:05')
    expect(formatarTempo(-3)).toBe('0:00')
  })
})

describe('useFalaProgresso', () => {
  it('estima a duracao pelo numero de palavras (147 palavras a 155*0,95 por minuto = 60s)', () => {
    const { result } = renderHook(() => useFalaProgresso(TEXTO))

    expect(result.current.total).toBe(60)
    expect(result.current.estado).toBe('parado')
  })

  it('alternar comeca a falar e o tempo avanca', () => {
    const { result } = renderHook(() => useFalaProgresso(TEXTO))

    act(() => result.current.alternar())
    act(() => vi.advanceTimersByTime(3000))

    expect(result.current.estado).toBe('falando')
    expect(ultimaFala?.text).toBe(TEXTO)
    expect(Math.round(result.current.decorrido)).toBe(3)
  })

  it('pausar congela o tempo e continuar retoma sem falar do zero', () => {
    const { result } = renderHook(() => useFalaProgresso(TEXTO))
    act(() => result.current.alternar())
    act(() => vi.advanceTimersByTime(2000))

    act(() => result.current.alternar())
    const aoPausar = result.current.decorrido
    act(() => vi.advanceTimersByTime(5000))

    expect(result.current.estado).toBe('pausado')
    expect(sintese.pause).toHaveBeenCalled()
    expect(result.current.decorrido).toBe(aoPausar)

    act(() => result.current.alternar())

    expect(result.current.estado).toBe('falando')
    expect(sintese.resume).toHaveBeenCalled()
    expect(sintese.speak).toHaveBeenCalledTimes(1)
  })

  it('ao terminar a fala volta ao inicio e zera o tempo', () => {
    const { result } = renderHook(() => useFalaProgresso(TEXTO))
    act(() => result.current.alternar())
    act(() => vi.advanceTimersByTime(2000))

    act(() => ultimaFala?.onend?.())

    expect(result.current.estado).toBe('parado')
    expect(result.current.decorrido).toBe(0)
  })

  it('cancela a fala ao desmontar se ele a iniciou', () => {
    const { result, unmount } = renderHook(() => useFalaProgresso(TEXTO))
    act(() => result.current.alternar())
    sintese.cancel.mockClear()

    unmount()

    expect(sintese.cancel).toHaveBeenCalledTimes(1)
  })

  it('nao cancela ao desmontar se nunca falou', () => {
    const { unmount } = renderHook(() => useFalaProgresso(TEXTO))

    unmount()

    expect(sintese.cancel).not.toHaveBeenCalled()
  })
})
