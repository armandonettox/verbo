import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ErroApi, listarLivros, obterCapitulo } from '../api/cliente.ts'
import type { Capitulo, Livro } from '../api/tipos.ts'
import { AudioProgresso } from '../componentes/AudioProgresso.tsx'
import { BarraResultados } from '../componentes/BarraResultados.tsx'
import { BotaoRolagem } from '../componentes/BotaoRolagem.tsx'
import { NavegacaoCapitulos } from '../componentes/NavegacaoCapitulos.tsx'
import { Quadro } from '../componentes/Quadro.tsx'
import { SeletorCapitulo } from '../componentes/SeletorCapitulo.tsx'
import { useBusca } from '../hooks/useBusca.ts'

type Resultado =
  | { chave: string; capitulo: Capitulo }
  | { chave: string; erro: string }

function Texto({ capitulo, livros }: { capitulo: Capitulo; livros: Livro[] | null }) {
  const textoAudio = capitulo.versiculos.map((v) => v.texto).join(' ')
  const chave = `${capitulo.livro}-${capitulo.capitulo}`

  return (
    <>
      <div className="titulo-capitulo">
        <h2>
          {capitulo.livro} {capitulo.capitulo}
        </h2>
        {/* a key reinicia o leitor ao trocar de capitulo */}
        <AudioProgresso key={chave} texto={textoAudio} />
      </div>
      <div className="texto-capitulo">
        {capitulo.versiculos.map((v) => (
          <p key={v.versiculo}>
            <strong>{v.versiculo}.</strong> {v.texto}
          </p>
        ))}
      </div>
      {/* sem a lista de livros (falha na API) a navegacao some, sem atrapalhar a leitura */}
      {livros && <NavegacaoCapitulos livros={livros} livro={capitulo.livro} capitulo={capitulo.capitulo} />}
      {/* a key para a rolagem automatica ao trocar de capitulo */}
      <BotaoRolagem key={chave} />
    </>
  )
}

export function Leitura() {
  const { livro = '', capitulo = '' } = useParams()
  const { conversa, novaBusca } = useBusca()
  const [resultado, setResultado] = useState<Resultado | null>(null)
  const [livros, setLivros] = useState<Livro[] | null>(null)

  const numero = Number(capitulo)
  const chave = `${livro}/${capitulo}`
  const numeroValido = Number.isInteger(numero) && numero > 0

  // Ao abrir ou trocar de capitulo a leitura comeca no topo
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [chave])

  useEffect(() => {
    let cancelado = false
    async function carregar() {
      try {
        const lista = await listarLivros()
        if (!cancelado) setLivros(lista)
      } catch {
        // so a navegacao entre capitulos depende da lista; a leitura segue sem ela
      }
    }
    carregar()
    return () => {
      cancelado = true
    }
  }, [])

  useEffect(() => {
    if (!numeroValido) return
    let cancelado = false
    async function carregar() {
      try {
        const dados = await obterCapitulo(livro, numero)
        if (!cancelado) setResultado({ chave, capitulo: dados })
      } catch (e) {
        if (cancelado) return
        const naoEncontrado = e instanceof ErroApi && e.status === 404
        setResultado({
          chave,
          erro: naoEncontrado
            ? 'Capitulo nao encontrado.'
            : e instanceof Error
              ? e.message
              : 'Nao foi possivel carregar o capitulo.',
        })
      }
    }
    carregar()
    return () => {
      cancelado = true
    }
  }, [livro, numero, numeroValido, chave])

  // Com uma busca em andamento, a barra continua mostrando os versiculos encontrados
  const barra = conversa ? (
    <BarraResultados
      pergunta={conversa.pergunta}
      versiculos={conversa.resultado.versiculos}
      onNovaBusca={novaBusca}
    />
  ) : (
    <SeletorCapitulo livroInicial={livro} capituloInicial={numeroValido ? numero : 1} />
  )

  // Resultado de outro capitulo (navegacao em andamento) conta como carregando
  const atual = resultado && resultado.chave === chave ? resultado : null

  return (
    <Quadro barra={barra}>
      <Link to="/" className="botao-secundario voltar">
        Voltar para busca
      </Link>

      {!numeroValido ? (
        <p className="erro" role="alert">
          Capitulo nao encontrado.
        </p>
      ) : !atual ? (
        <p className="texto-mutado" role="status">
          Carregando...
        </p>
      ) : 'erro' in atual ? (
        <p className="erro" role="alert">
          {atual.erro}
        </p>
      ) : (
        <Texto capitulo={atual.capitulo} livros={livros} />
      )}
    </Quadro>
  )
}
