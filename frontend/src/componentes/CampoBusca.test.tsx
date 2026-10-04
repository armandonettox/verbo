import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { CampoBusca } from './CampoBusca.tsx'

function digitar(texto: string) {
  fireEvent.change(screen.getByLabelText('Qual e a sua pergunta?'), { target: { value: texto } })
}

describe('CampoBusca', () => {
  it('envia a pergunta sem espacos nas pontas', () => {
    const onBuscar = vi.fn()
    render(<CampoBusca buscando={false} onBuscar={onBuscar} />)

    digitar('  como orar?  ')
    fireEvent.click(screen.getByRole('button', { name: 'Buscar' }))

    expect(onBuscar).toHaveBeenCalledWith('como orar?')
  })

  it('nao envia pergunta vazia ou so com espacos', () => {
    const onBuscar = vi.fn()
    render(<CampoBusca buscando={false} onBuscar={onBuscar} />)

    digitar('   ')
    fireEvent.click(screen.getByRole('button', { name: 'Buscar' }))

    expect(onBuscar).not.toHaveBeenCalled()
  })

  it('enter no campo envia a busca', () => {
    const onBuscar = vi.fn()
    render(<CampoBusca buscando={false} onBuscar={onBuscar} />)

    digitar('quem foi Davi')
    fireEvent.submit(screen.getByRole('button', { name: 'Buscar' }).closest('form')!)

    expect(onBuscar).toHaveBeenCalledWith('quem foi Davi')
  })

  it('enquanto busca, o botao fica desabilitado e mostra Buscando', () => {
    render(<CampoBusca buscando={true} onBuscar={vi.fn()} />)

    const botao = screen.getByRole('button', { name: 'Buscando' })
    expect(botao).toBeDisabled()
  })

  it('limita a pergunta a 500 caracteres, como a API', () => {
    render(<CampoBusca buscando={false} onBuscar={vi.fn()} />)

    expect(screen.getByLabelText('Qual e a sua pergunta?')).toHaveProperty('maxLength', 500)
  })
})
