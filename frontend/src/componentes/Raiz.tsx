import { Outlet } from 'react-router-dom'
import { BotaoTema } from './BotaoTema.tsx'

// Casca comum a todas as paginas: botao de tema e o conteudo da rota
export function Raiz() {
  return (
    <>
      <BotaoTema />
      <Outlet />
    </>
  )
}
