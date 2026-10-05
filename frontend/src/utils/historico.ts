// As ultimas buscas ficam so neste navegador (localStorage). O servidor nao guarda pergunta nenhuma.
const CHAVE = 'verbo-historico-buscas'
export const MAX_HISTORICO = 10

export function lerHistorico(): string[] {
  try {
    const bruto = localStorage.getItem(CHAVE)
    if (!bruto) return []
    const lista: unknown = JSON.parse(bruto)
    if (!Array.isArray(lista)) return []
    return lista.filter((p): p is string => typeof p === 'string' && p.trim() !== '').slice(0, MAX_HISTORICO)
  } catch {
    return []
  }
}

function gravar(lista: string[]) {
  try {
    localStorage.setItem(CHAVE, JSON.stringify(lista))
  } catch {
    // sem armazenamento: o historico simplesmente nao e guardado
  }
}

// A mais recente fica no topo; repetir uma pergunta so a traz de volta para o topo
export function adicionarAoHistorico(pergunta: string): string[] {
  const texto = pergunta.trim()
  if (!texto) return lerHistorico()
  const chave = texto.toLocaleLowerCase('pt-BR')
  const lista = [texto, ...lerHistorico().filter((p) => p.toLocaleLowerCase('pt-BR') !== chave)].slice(
    0,
    MAX_HISTORICO,
  )
  gravar(lista)
  return lista
}

export function limparHistorico() {
  try {
    localStorage.removeItem(CHAVE)
  } catch {
    // sem armazenamento: nada a apagar
  }
}
