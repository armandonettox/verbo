import { act, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { Quadro } from './Quadro.tsx'

type Ouvinte = () => void

// matchMedia controlavel: o teste escolhe se a tela e estreita e pode "redimensionar"
function simularTela(estreitaInicial: boolean) {
  let estreita = estreitaInicial
  const ouvintes = new Set<Ouvinte>()
  vi.stubGlobal(
    'matchMedia',
    vi.fn(() => ({
      get matches() {
        return estreita
      },
      addEventListener: (_: string, fn: Ouvinte) => ouvintes.add(fn),
      removeEventListener: (_: string, fn: Ouvinte) => ouvintes.delete(fn),
    })),
  )
  return {
    redimensionar(paraEstreita: boolean) {
      estreita = paraEstreita
      act(() => ouvintes.forEach((fn) => fn()))
    },
  }
}

function renderizar() {
  return render(
    <Quadro barra={<p>conteudo da barra</p>}>
      <p>conteudo principal</p>
    </Quadro>,
  )
}

const botao = () => screen.getByRole('button', { name: /barra lateral/i })
const barra = () => document.getElementById('barra-lateral')!

beforeEach(() => localStorage.clear())
afterEach(() => {
  vi.unstubAllGlobals()
  localStorage.clear()
})

describe('Quadro no computador', () => {
  beforeEach(() => simularTela(false))

  it('comeca com a barra aberta', () => {
    renderizar()

    expect(botao()).toHaveAttribute('aria-expanded', 'true')
    expect(botao()).toHaveAccessibleName('Fechar barra lateral')
    expect(barra()).not.toHaveAttribute('inert')
    expect(screen.getByText('conteudo da barra')).toBeVisible()
  })

  it('fecha e abre pelo botao, tirando a barra fechada da navegacao', () => {
    renderizar()

    fireEvent.click(botao())

    expect(botao()).toHaveAttribute('aria-expanded', 'false')
    expect(botao()).toHaveAccessibleName('Abrir barra lateral')
    expect(barra()).toHaveAttribute('inert')

    fireEvent.click(botao())

    expect(botao()).toHaveAttribute('aria-expanded', 'true')
    expect(barra()).not.toHaveAttribute('inert')
  })

  it('lembra a escolha ao abrir outra tela', () => {
    const primeira = renderizar()
    fireEvent.click(botao())
    expect(localStorage.getItem('barra-lateral')).toBe('fechada')
    primeira.unmount()

    renderizar()

    expect(botao()).toHaveAttribute('aria-expanded', 'false')
  })

  it('o conteudo principal continua na tela com a barra fechada', () => {
    renderizar()

    fireEvent.click(botao())

    expect(screen.getByText('conteudo principal')).toBeInTheDocument()
  })

  it('nao mostra o fundo escuro nem reage a Esc', () => {
    const { container } = renderizar()

    fireEvent.keyDown(document, { key: 'Escape' })

    expect(botao()).toHaveAttribute('aria-expanded', 'true')
    expect(container.querySelector('.barra-fundo')).toBeNull()
  })

  it('funciona com o localStorage bloqueado', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('bloqueado')
    })
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('bloqueado')
    })

    renderizar()
    expect(botao()).toHaveAttribute('aria-expanded', 'true')

    expect(() => fireEvent.click(botao())).not.toThrow()
    expect(botao()).toHaveAttribute('aria-expanded', 'false')
  })
})

describe('Quadro no celular', () => {
  beforeEach(() => simularTela(true))

  it('comeca com a gaveta fechada, mesmo que o computador tenha deixado aberta', () => {
    localStorage.setItem('barra-lateral', 'aberta')

    const { container } = renderizar()

    expect(botao()).toHaveAttribute('aria-expanded', 'false')
    expect(barra()).toHaveAttribute('inert')
    expect(container.querySelector('.barra-fundo')).toBeNull()
  })

  it('abre com o botao e mostra o fundo escuro', () => {
    const { container } = renderizar()

    fireEvent.click(botao())

    expect(botao()).toHaveAttribute('aria-expanded', 'true')
    expect(container.querySelector('.barra-fundo')).not.toBeNull()
  })

  it('fecha ao tocar no fundo escuro', () => {
    const { container } = renderizar()
    fireEvent.click(botao())

    fireEvent.click(container.querySelector('.barra-fundo')!)

    expect(botao()).toHaveAttribute('aria-expanded', 'false')
    expect(container.querySelector('.barra-fundo')).toBeNull()
  })

  it('fecha com Esc', () => {
    renderizar()
    fireEvent.click(botao())

    fireEvent.keyDown(document, { key: 'Escape' })

    expect(botao()).toHaveAttribute('aria-expanded', 'false')
  })

  it('outras teclas nao fecham', () => {
    renderizar()
    fireEvent.click(botao())

    fireEvent.keyDown(document, { key: 'Enter' })

    expect(botao()).toHaveAttribute('aria-expanded', 'true')
  })

  it('nao grava a escolha do celular (nao muda o que vale no computador)', () => {
    renderizar()

    fireEvent.click(botao())

    expect(localStorage.getItem('barra-lateral')).toBeNull()
  })
})

describe('Quadro ao redimensionar a janela', () => {
  it('fecha a gaveta ao virar tela estreita e restaura a escolha ao voltar', () => {
    const tela = simularTela(false)
    localStorage.setItem('barra-lateral', 'aberta')
    renderizar()
    expect(botao()).toHaveAttribute('aria-expanded', 'true')

    tela.redimensionar(true)
    expect(botao()).toHaveAttribute('aria-expanded', 'false')

    tela.redimensionar(false)
    expect(botao()).toHaveAttribute('aria-expanded', 'true')
  })

  it('ao voltar ao computador respeita a escolha salva de fechada', () => {
    const tela = simularTela(true)
    localStorage.setItem('barra-lateral', 'fechada')
    renderizar()

    tela.redimensionar(false)

    expect(botao()).toHaveAttribute('aria-expanded', 'false')
  })
})
