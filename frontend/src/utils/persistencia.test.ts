import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Conversa, TurnoChat } from '../contexto/buscaContexto.ts'
import { apagarConversa, lerConversa, salvarConversa } from './persistencia.ts'

const CHAVE = 'verbo-conversa'

function conversa(sobrescrever: Partial<Conversa> = {}): Conversa {
  return {
    pergunta: 'como orar?',
    resultado: {
      pergunta: 'como orar?',
      modo: 'nvidia',
      aviso: null,
      versiculos: [
        { referencia: 'São Lucas 11:1-12', texto: 'Senhor, ensina-nos a orar.', similaridade: 66.3, livro: 'São Lucas', capitulo: 11 },
      ],
    },
    resposta: 'Jesus ensinou o Pai Nosso.',
    citacoes: ['São Mateus 7'],
    quando: new Date('2026-10-05T10:00:00'),
    ...sobrescrever,
  }
}

const turnos: TurnoChat[] = [
  { role: 'user', content: 'e depois?', quando: new Date('2026-10-05T10:01:00') },
  { role: 'assistant', content: 'Depois...', citacoes: ['São João 3'], quando: new Date('2026-10-05T10:01:30') },
]

afterEach(() => {
  sessionStorage.clear()
  vi.restoreAllMocks()
})

describe('persistencia da conversa', () => {
  it('guarda e devolve a conversa e o historico, com as datas de volta como Date', () => {
    salvarConversa(conversa(), turnos)

    const lida = lerConversa()!

    expect(lida.conversa.pergunta).toBe('como orar?')
    expect(lida.conversa.resposta).toBe('Jesus ensinou o Pai Nosso.')
    expect(lida.conversa.citacoes).toEqual(['São Mateus 7'])
    expect(lida.conversa.quando).toBeInstanceOf(Date)
    expect(lida.conversa.quando.toISOString()).toBe(new Date('2026-10-05T10:00:00').toISOString())
    expect(lida.conversa.resultado.versiculos).toHaveLength(1)
    expect(lida.historico).toHaveLength(2)
    expect(lida.historico[1].citacoes).toEqual(['São João 3'])
    expect(lida.historico[0].quando).toBeInstanceOf(Date)
  })

  it('aceita conversa sem resposta (modo local ou resposta que falhou)', () => {
    salvarConversa(conversa({ resposta: null }), [])
    expect(lerConversa()!.conversa.resposta).toBeNull()
  })

  it('sem nada guardado devolve null', () => {
    expect(lerConversa()).toBeNull()
  })

  it('apagar remove o que estava guardado', () => {
    salvarConversa(conversa(), [])
    apagarConversa()
    expect(lerConversa()).toBeNull()
  })

  it.each([
    ['json quebrado', '{nao e json'],
    ['versao diferente', JSON.stringify({ versao: 99, conversa: {}, historico: [] })],
    ['sem versiculos', JSON.stringify({ versao: 1, conversa: { pergunta: 'x', resultado: {}, resposta: null, quando: '2026-10-05T10:00:00' }, historico: [] })],
    ['data invalida', JSON.stringify({ versao: 1, conversa: { pergunta: 'x', resultado: { versiculos: [] }, resposta: null, quando: 'ontem' }, historico: [] })],
    ['historico que nao e lista', JSON.stringify({ versao: 1, conversa: { pergunta: 'x', resultado: { versiculos: [] }, resposta: null, quando: '2026-10-05T10:00:00' }, historico: 'x' })],
    ['turno com papel invalido', JSON.stringify({ versao: 1, conversa: { pergunta: 'x', resultado: { versiculos: [] }, resposta: null, quando: '2026-10-05T10:00:00' }, historico: [{ role: 'robo', content: 'a', quando: '2026-10-05T10:00:00' }] })],
  ])('conteudo invalido (%s) vira null em vez de quebrar a tela', (_nome, bruto) => {
    sessionStorage.setItem(CHAVE, bruto)
    expect(lerConversa()).toBeNull()
  })

  it('conversa antiga sem o campo de citacoes volta com lista vazia', () => {
    salvarConversa(conversa(), [])
    const salvo = JSON.parse(sessionStorage.getItem(CHAVE)!)
    delete salvo.conversa.citacoes
    sessionStorage.setItem(CHAVE, JSON.stringify(salvo))

    expect(lerConversa()!.conversa.citacoes).toEqual([])
  })

  it('armazenamento bloqueado nao derruba: salvar e ignorado e ler devolve null', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new DOMException('cheio', 'QuotaExceededError')
    })
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new DOMException('bloqueado', 'SecurityError')
    })

    expect(() => salvarConversa(conversa(), [])).not.toThrow()
    expect(lerConversa()).toBeNull()
  })
})
