import { BarraResultados } from '../componentes/BarraResultados.tsx'
import { CampoAcompanhamento } from '../componentes/CampoAcompanhamento.tsx'
import { CampoBusca } from '../componentes/CampoBusca.tsx'
import { CartaoLeituraDia } from '../componentes/CartaoLeituraDia.tsx'
import { MensagemChat } from '../componentes/MensagemChat.tsx'
import { Quadro } from '../componentes/Quadro.tsx'
import { Rodape } from '../componentes/Rodape.tsx'
import { SeletorCapitulo } from '../componentes/SeletorCapitulo.tsx'
import { useBusca } from '../hooks/useBusca.ts'

// A API aceita ate 20 turnos de historico
const MAX_TURNOS = 20

function Inicio() {
  const { buscando, erro, buscar } = useBusca()

  return (
    <Quadro
      barra={
        <>
          <p className="texto-mutado">
            Escolha um livro e capitulo abaixo para ler o texto completo, ou use a busca ao lado
            para encontrar versiculos por tema.
          </p>
          <SeletorCapitulo />
        </>
      }
    >
      <div className="bloco-central">
        <img className="logo-central" src="/logo.png" alt="Verbo" width={90} height={90} />
        <h1>Explore a Biblia</h1>
        <p>
          <em>
            Pergunte e descubra passagens biblicas com compreensao semantica e insights
            contextuais.
          </em>
        </p>
      </div>
      <CampoBusca buscando={buscando} onBuscar={buscar} />
      {erro && (
        <p className="erro" role="alert">
          {erro}
        </p>
      )}
      <CartaoLeituraDia />
      <Rodape />
    </Quadro>
  )
}

function ConversaAtual() {
  const {
    conversa,
    historico,
    gerando,
    erroChat,
    perguntar,
    regenerarOriginal,
    regenerarTurno,
    novaBusca,
  } = useBusca()

  if (!conversa) return null
  const { resultado } = conversa
  const ocupado = gerando !== null
  const podeConversar = conversa.resposta !== null
  const limiteAtingido = historico.length >= MAX_TURNOS

  return (
    <Quadro
      barra={<BarraResultados versiculos={resultado.versiculos} onNovaBusca={novaBusca} />}
      rotuloVersiculos={`Ver versiculos (${resultado.versiculos.length})`}
    >
      <MensagemChat role="user" conteudo={conversa.pergunta} quando={conversa.quando} />

      {resultado.aviso && (
        <p className="aviso" role="status">
          {resultado.aviso}
        </p>
      )}

      {conversa.resposta !== null && (
        <MensagemChat
          role="assistant"
          conteudo={conversa.resposta}
          gerando={gerando === 'original'}
          onRegenerar={regenerarOriginal}
          desabilitado={ocupado}
        />
      )}

      {/* a busca funcionou mas a resposta falhou: da para tentar gerar de novo */}
      {conversa.resposta === null && gerando === 'original' && (
        <MensagemChat role="assistant" conteudo="" gerando />
      )}
      {conversa.resposta === null &&
        gerando !== 'original' &&
        resultado.modo === 'nvidia' &&
        resultado.versiculos.length > 0 && (
          <button type="button" className="botao-secundario" onClick={regenerarOriginal} disabled={ocupado}>
            Gerar resposta
          </button>
        )}

      {historico.map((turno, i) => (
        <MensagemChat
          key={i}
          role={turno.role}
          conteudo={turno.content}
          quando={turno.role === 'user' ? turno.quando : undefined}
          gerando={gerando === i}
          onRegenerar={turno.role === 'assistant' ? () => regenerarTurno(i) : undefined}
          desabilitado={ocupado}
        />
      ))}

      {gerando === 'novo' && (
        <MensagemChat role="assistant" conteudo="" gerando />
      )}

      {erroChat && (
        <p className="erro" role="alert">
          {erroChat}
        </p>
      )}

      {podeConversar &&
        (limiteAtingido ? (
          <p className="texto-mutado">
            Esta conversa chegou ao limite de perguntas. Use "Nova busca" para recomecar.
          </p>
        ) : (
          <CampoAcompanhamento ocupado={ocupado} onEnviar={perguntar} />
        ))}
    </Quadro>
  )
}

export function Home() {
  const { conversa } = useBusca()
  return conversa ? <ConversaAtual /> : <Inicio />
}
