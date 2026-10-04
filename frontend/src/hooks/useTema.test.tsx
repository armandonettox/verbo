import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { useTema } from './useTema.ts'

beforeEach(() => {
  localStorage.clear()
  document.documentElement.removeAttribute('data-tema')
})

afterEach(() => {
  localStorage.clear()
  document.documentElement.removeAttribute('data-tema')
})

describe('useTema', () => {
  it('comeca no claro quando nada foi salvo', () => {
    const { result } = renderHook(() => useTema())

    expect(result.current.tema).toBe('claro')
    expect(document.documentElement.hasAttribute('data-tema')).toBe(false)
  })

  it('le o tema escuro salvo', () => {
    localStorage.setItem('tema', 'escuro')

    const { result } = renderHook(() => useTema())

    expect(result.current.tema).toBe('escuro')
    expect(document.documentElement.getAttribute('data-tema')).toBe('escuro')
  })

  it('alternar troca o atributo e salva a escolha', () => {
    const { result } = renderHook(() => useTema())

    act(() => result.current.alternar())

    expect(result.current.tema).toBe('escuro')
    expect(document.documentElement.getAttribute('data-tema')).toBe('escuro')
    expect(localStorage.getItem('tema')).toBe('escuro')

    act(() => result.current.alternar())

    expect(result.current.tema).toBe('claro')
    expect(document.documentElement.hasAttribute('data-tema')).toBe(false)
    expect(localStorage.getItem('tema')).toBe('claro')
  })

  it('valor salvo desconhecido volta para o claro', () => {
    localStorage.setItem('tema', 'roxo')

    const { result } = renderHook(() => useTema())

    expect(result.current.tema).toBe('claro')
  })
})
