import { Link } from 'react-router-dom'
import { formatarQuando } from '../utils/texto.ts'
import { AcoesMensagem } from './AcoesMensagem.tsx'
import { Markdown } from './Markdown.tsx'

interface MensagemChatProps {
  role: 'user' | 'assistant'
  conteudo: string
  // so a pergunta do usuario mostra o horario
  quando?: Date
  gerando?: boolean
  // Capitulos citados pela IA que nao estavam entre os versiculos encontrados
  citacoesNaoConfirmadas?: string[]
  onRegenerar?: () => void
  desabilitado?: boolean
}

// "Sao Mateus 7" vira o link para ler o capitulo e conferir
function AvisoCitacoes({ citacoes }: { citacoes: string[] }) {
  return (
    <p className="aviso aviso-citacoes" role="note">
      Atencao: esta resposta cita passagens que nao estavam entre os versiculos encontrados:{' '}
      {citacoes.map((citacao, i) => {
        const corte = citacao.lastIndexOf(' ')
        const livro = citacao.slice(0, corte)
        const capitulo = citacao.slice(corte + 1)
        return (
          <span key={citacao}>
            {i > 0 && ', '}
            <Link to={`/ler/${encodeURIComponent(livro)}/${capitulo}`}>{citacao}</Link>
          </span>
        )
      })}
      . Confira no texto da Biblia antes de confiar nelas.
    </p>
  )
}

export function MensagemChat({
  role,
  conteudo,
  quando,
  gerando,
  citacoesNaoConfirmadas = [],
  onRegenerar,
  desabilitado,
}: MensagemChatProps) {
  if (role === 'user') {
    return (
      <div className="mensagem mensagem-usuario">
        {quando && <span className="mensagem-quando">{formatarQuando(quando)}</span>}
        <p className="balao">{conteudo}</p>
      </div>
    )
  }

  return (
    <div className="mensagem mensagem-assistente">
      {gerando ? (
        <p className="texto-mutado" role="status">
          Gerando resposta...
        </p>
      ) : (
        <>
          <Markdown texto={conteudo} />
          {citacoesNaoConfirmadas.length > 0 && (
            <AvisoCitacoes citacoes={citacoesNaoConfirmadas} />
          )}
          <AcoesMensagem markdown={conteudo} onRegenerar={onRegenerar} desabilitado={desabilitado} />
        </>
      )}
    </div>
  )
}
