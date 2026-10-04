import { useEffect, useState } from 'react'
import { versiculoDoDia } from '../api/cliente.ts'
import type { VersiculoDia } from '../api/tipos.ts'
import { BotaoAudio } from './BotaoAudio.tsx'

type Estado =
  | { situacao: 'carregando' }
  | { situacao: 'pronto'; versiculo: VersiculoDia }
  | { situacao: 'indisponivel' }

export function CartaoLeituraDia() {
  const [estado, setEstado] = useState<Estado>({ situacao: 'carregando' })

  useEffect(() => {
    let cancelado = false
    async function carregar() {
      try {
        const versiculo = await versiculoDoDia()
        if (!cancelado) setEstado({ situacao: 'pronto', versiculo })
      } catch {
        if (!cancelado) setEstado({ situacao: 'indisponivel' })
      }
    }
    carregar()
    return () => {
      cancelado = true
    }
  }, [])

  if (estado.situacao === 'indisponivel') return null

  return (
    <section className="cartao cartao-leitura-dia" aria-label="Leitura do dia">
      <p className="rotulo-cartao">LEITURA DO DIA</p>
      {estado.situacao === 'carregando' ? (
        <p className="texto-mutado">Carregando...</p>
      ) : (
        <>
          <div className="cartao-acoes">
            <BotaoAudio texto={estado.versiculo.texto} />
          </div>
          <p>
            <strong>{estado.versiculo.referencia}</strong>
          </p>
          <p>{estado.versiculo.texto}</p>
        </>
      )}
    </section>
  )
}
