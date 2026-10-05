import { afterEach, describe, expect, it, vi } from 'vitest'
import { adicionarAoHistorico, lerHistorico, limparHistorico, MAX_HISTORICO } from './historico.ts'

afterEach(() => {
  localStorage.clear()
  vi.restoreAllMocks()
})

describe('historico de buscas', () => {
  it('comeca vazio', () => {
    expect(lerHistorico()).toEqual([])
  })

  it('a busca mais recente fica no topo', () => {
    adicionarAoHistorico('primeira')
    adicionarAoHistorico('segunda')
    expect(lerHistorico()).toEqual(['segunda', 'primeira'])
  })

  it('repetir uma pergunta so a traz de volta para o topo, sem duplicar nem ligar para a caixa', () => {
    adicionarAoHistorico('Como orar?')
    adicionarAoHistorico('outra')
    adicionarAoHistorico('como orar?')
    expect(lerHistorico()).toEqual(['como orar?', 'outra'])
  })

  it('guarda no maximo 10, descartando as mais antigas', () => {
    for (let i = 1; i <= MAX_HISTORICO + 3; i++) adicionarAoHistorico(`pergunta ${i}`)
    const lista = lerHistorico()
    expect(lista).toHaveLength(MAX_HISTORICO)
    expect(lista[0]).toBe(`pergunta ${MAX_HISTORICO + 3}`)
    expect(lista).not.toContain('pergunta 1')
  })

  it('ignora pergunta vazia e tira espacos das pontas', () => {
    adicionarAoHistorico('   ')
    adicionarAoHistorico('  com espacos  ')
    expect(lerHistorico()).toEqual(['com espacos'])
  })

  it('limpar apaga tudo', () => {
    adicionarAoHistorico('algo')
    limparHistorico()
    expect(lerHistorico()).toEqual([])
  })

  it('conteudo corrompido ou de outro formato vira lista vazia', () => {
    localStorage.setItem('verbo-historico-buscas', '{quebrado')
    expect(lerHistorico()).toEqual([])
    localStorage.setItem('verbo-historico-buscas', JSON.stringify({ a: 1 }))
    expect(lerHistorico()).toEqual([])
    localStorage.setItem('verbo-historico-buscas', JSON.stringify(['ok', 5, null, '  ']))
    expect(lerHistorico()).toEqual(['ok'])
  })

  it('armazenamento bloqueado nao derruba', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new DOMException('cheio', 'QuotaExceededError')
    })
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new DOMException('bloqueado', 'SecurityError')
    })
    expect(() => adicionarAoHistorico('algo')).not.toThrow()
    expect(lerHistorico()).toEqual([])
  })
})
