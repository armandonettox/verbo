import { describe, expect, it } from 'vitest'
import { formatarQuando, resumirTexto, textoSemMarkdown } from './texto.ts'

describe('resumirTexto', () => {
  it('nao mexe em texto curto', () => {
    expect(resumirTexto('Pai nosso', 220)).toBe('Pai nosso')
  })

  it('corta sem quebrar palavra e acrescenta reticencias', () => {
    expect(resumirTexto('um dois tres quatro', 10)).toBe('um dois...')
  })
})

describe('textoSemMarkdown', () => {
  it('tira negrito, titulos, listas e codigo', () => {
    const md = '## Titulo\n- **Ele ensinou** a orar\n* outro `item`'
    expect(textoSemMarkdown(md)).toBe('Titulo\nEle ensinou a orar\noutro item')
  })
})

describe('formatarQuando', () => {
  const hoje = new Date(2026, 9, 3, 15, 0)

  it('usa Hoje para o mesmo dia', () => {
    expect(formatarQuando(new Date(2026, 9, 3, 9, 5), hoje)).toMatch(/^Hoje 09:05$/)
  })

  it('usa a data para outro dia', () => {
    expect(formatarQuando(new Date(2026, 9, 2, 9, 5), hoje)).toBe('02/10/2026 09:05')
  })
})
