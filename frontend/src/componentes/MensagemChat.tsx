import { formatarQuando } from '../utils/texto.ts'
import { AcoesMensagem } from './AcoesMensagem.tsx'
import { Markdown } from './Markdown.tsx'

interface MensagemChatProps {
  role: 'user' | 'assistant'
  conteudo: string
  // so a pergunta do usuario mostra o horario
  quando?: Date
  gerando?: boolean
  onRegenerar?: () => void
  desabilitado?: boolean
}

export function MensagemChat({
  role,
  conteudo,
  quando,
  gerando,
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
          <AcoesMensagem markdown={conteudo} onRegenerar={onRegenerar} desabilitado={desabilitado} />
        </>
      )}
    </div>
  )
}
