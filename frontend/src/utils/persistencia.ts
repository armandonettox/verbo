import type { Conversa, TurnoChat } from '../contexto/buscaContexto.ts'

// A conversa fica na aba (sessionStorage): sobrevive a recarregar a pagina, mas nao vai para
// outras abas nem fica guardada depois que a aba fecha.
const CHAVE = 'verbo-conversa'
const VERSAO = 1

interface TurnoSalvo extends Omit<TurnoChat, 'quando'> {
  quando: string
}

interface ConversaSalva extends Omit<Conversa, 'quando'> {
  quando: string
}

interface Salvo {
  versao: number
  conversa: ConversaSalva
  historico: TurnoSalvo[]
}

export interface ConversaRestaurada {
  conversa: Conversa
  historico: TurnoChat[]
}

export function salvarConversa(conversa: Conversa, historico: TurnoChat[]) {
  const salvo: Salvo = {
    versao: VERSAO,
    conversa: { ...conversa, quando: conversa.quando.toISOString() },
    historico: historico.map((t) => ({ ...t, quando: t.quando.toISOString() })),
  }
  try {
    sessionStorage.setItem(CHAVE, JSON.stringify(salvo))
  } catch {
    // armazenamento cheio ou bloqueado: a conversa so nao sobrevive ao recarregar
  }
}

export function apagarConversa() {
  try {
    sessionStorage.removeItem(CHAVE)
  } catch {
    // sem armazenamento: nada a apagar
  }
}

function dataValida(texto: unknown): Date | null {
  if (typeof texto !== 'string') return null
  const data = new Date(texto)
  return Number.isNaN(data.getTime()) ? null : data
}

// Le com cuidado: o que estiver guardado pode ser de uma versao antiga ou estar corrompido,
// e nesse caso a tela simplesmente comeca do zero.
export function lerConversa(): ConversaRestaurada | null {
  try {
    const bruto = sessionStorage.getItem(CHAVE)
    if (!bruto) return null
    const salvo = JSON.parse(bruto) as Partial<Salvo>
    if (salvo.versao !== VERSAO || !salvo.conversa || !Array.isArray(salvo.historico)) return null

    const { conversa } = salvo
    const quando = dataValida(conversa.quando)
    const resultado = conversa.resultado
    if (
      !quando ||
      typeof conversa.pergunta !== 'string' ||
      !resultado ||
      !Array.isArray(resultado.versiculos) ||
      (conversa.resposta !== null && typeof conversa.resposta !== 'string')
    ) {
      return null
    }

    const historico: TurnoChat[] = []
    for (const turno of salvo.historico) {
      const quandoTurno = dataValida(turno.quando)
      if (!quandoTurno || typeof turno.content !== 'string' || !['user', 'assistant'].includes(turno.role)) {
        return null
      }
      historico.push({ ...turno, quando: quandoTurno })
    }

    return {
      conversa: {
        ...conversa,
        citacoes: Array.isArray(conversa.citacoes) ? conversa.citacoes : [],
        quando,
      },
      historico,
    }
  } catch {
    return null
  }
}
