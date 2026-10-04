import { useCallback, useEffect, useState } from 'react'

export type Tema = 'claro' | 'escuro'

const CHAVE = 'tema'

function lerTemaSalvo(): Tema {
  try {
    return localStorage.getItem(CHAVE) === 'escuro' ? 'escuro' : 'claro'
  } catch {
    // localStorage pode estar bloqueado (aba privada, cookies desativados)
    return 'claro'
  }
}

// O index.html ja aplica o tema salvo antes do React carregar; aqui o estado
// acompanha o atributo e persiste a escolha
export function useTema() {
  const [tema, setTema] = useState<Tema>(lerTemaSalvo)

  useEffect(() => {
    if (tema === 'escuro') {
      document.documentElement.setAttribute('data-tema', 'escuro')
    } else {
      document.documentElement.removeAttribute('data-tema')
    }
    try {
      localStorage.setItem(CHAVE, tema)
    } catch {
      // sem persistencia, o tema vale so ate fechar a aba
    }
  }, [tema])

  const alternar = useCallback(() => {
    setTema((atual) => (atual === 'claro' ? 'escuro' : 'claro'))
  }, [])

  return { tema, alternar }
}
