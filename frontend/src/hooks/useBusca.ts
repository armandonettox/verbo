import { useContext } from 'react'
import { BuscaContexto } from '../contexto/buscaContexto.ts'

export function useBusca() {
  const contexto = useContext(BuscaContexto)
  if (!contexto) throw new Error('useBusca precisa estar dentro de BuscaProvider')
  return contexto
}
