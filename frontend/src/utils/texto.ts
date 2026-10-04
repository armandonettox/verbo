const TAMANHO_RESUMO = 220

// Mesmo corte do app antigo: ate o tamanho, sem quebrar palavra no meio
export function resumirTexto(texto: string, tamanho = TAMANHO_RESUMO): string {
  if (texto.length <= tamanho) return texto
  const corte = texto.slice(0, tamanho)
  const ultimoEspaco = corte.lastIndexOf(' ')
  return (ultimoEspaco > 0 ? corte.slice(0, ultimoEspaco) : corte) + '...'
}

// A resposta vem em markdown; para ouvir ou copiar como texto, tira a marcacao
export function textoSemMarkdown(markdown: string): string {
  return markdown
    .replace(/^\s{0,3}#{1,6}\s+/gm, '')
    .replace(/^\s*[-*+]\s+/gm, '')
    .replace(/(\*\*|__)(.*?)\1/g, '$2')
    .replace(/(\*|_)(.*?)\1/g, '$2')
    .replace(/`([^`]*)`/g, '$1')
    .trim()
}

export function formatarQuando(quando: Date, hoje: Date = new Date()): string {
  const hora = quando.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  const mesmoDia =
    quando.getFullYear() === hoje.getFullYear() &&
    quando.getMonth() === hoje.getMonth() &&
    quando.getDate() === hoje.getDate()
  if (mesmoDia) return `Hoje ${hora}`
  return `${quando.toLocaleDateString('pt-BR')} ${hora}`
}
