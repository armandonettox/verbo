import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  buscar,
  dataLocalISO,
  ErroApi,
  limparCacheLivros,
  listarLivros,
  obterCapitulo,
  versiculoDoDia,
} from './cliente.ts'

function respostaJson(corpo: unknown, status = 200) {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

afterEach(() => {
  vi.unstubAllGlobals()
  limparCacheLivros()
})

describe('dataLocalISO', () => {
  it('formata a data local com zeros a esquerda', () => {
    expect(dataLocalISO(new Date(2026, 0, 5))).toBe('2026-01-05')
  })

  it('usa o dia local, nao o dia em UTC', () => {
    // 23h30 no horario local ainda e o mesmo dia, mesmo que em UTC ja seja o seguinte
    expect(dataLocalISO(new Date(2026, 9, 3, 23, 30))).toBe('2026-10-03')
  })
})

describe('buscar', () => {
  it('envia a pergunta por POST em JSON', async () => {
    const fetchFalso = vi.fn().mockResolvedValue(
      respostaJson({ pergunta: 'x', modo: 'nvidia', resposta: 'ok', aviso: null, versiculos: [] }),
    )
    vi.stubGlobal('fetch', fetchFalso)

    const resultado = await buscar('como orar?')

    expect(resultado.modo).toBe('nvidia')
    const [caminho, opcoes] = fetchFalso.mock.calls[0]
    expect(caminho).toBe('/api/buscar')
    expect(opcoes.method).toBe('POST')
    expect(JSON.parse(opcoes.body)).toEqual({ pergunta: 'como orar?' })
  })

  it('usa a mensagem em portugues que a API manda no 503', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(respostaJson({ detail: 'O servico de IA esta indisponivel.' }, 503)),
    )

    const erro = await buscar('como orar?').catch((e) => e)

    expect(erro).toBeInstanceOf(ErroApi)
    expect(erro.status).toBe(503)
    expect(erro.message).toBe('O servico de IA esta indisponivel.')
  })

  it('cai na mensagem padrao quando o 422 traz lista de erros', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(respostaJson({ detail: [{ msg: 'campo invalido' }] }, 422)),
    )

    const erro = await buscar('a').catch((e) => e)

    expect(erro.status).toBe(422)
    expect(erro.message).toContain('Nao foi possivel')
  })

  it('trata falha de rede como erro com status 0', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    const erro = await buscar('como orar?').catch((e) => e)

    expect(erro).toBeInstanceOf(ErroApi)
    expect(erro.status).toBe(0)
    expect(erro.message).toContain('conectar')
  })
})

describe('leitura', () => {
  it('codifica o nome do livro com acento e espaco na URL', async () => {
    const fetchFalso = vi.fn().mockResolvedValue(respostaJson({}))
    vi.stubGlobal('fetch', fetchFalso)

    await obterCapitulo('São Lucas', 11)

    expect(fetchFalso.mock.calls[0][0]).toBe('/api/capitulos/S%C3%A3o%20Lucas/11')
  })

  it('envia a data local no versiculo do dia', async () => {
    const fetchFalso = vi.fn().mockResolvedValue(respostaJson({}))
    vi.stubGlobal('fetch', fetchFalso)

    await versiculoDoDia('2026-10-03')

    expect(fetchFalso.mock.calls[0][0]).toBe('/api/versiculo-do-dia?data=2026-10-03')
  })
})

describe('listarLivros', () => {
  it('chama a API uma vez so e reaproveita a lista', async () => {
    const fetchFalso = vi.fn().mockImplementation(() => Promise.resolve(respostaJson([{ livro: 'Genesis' }])))
    vi.stubGlobal('fetch', fetchFalso)

    const [a, b] = await Promise.all([listarLivros(), listarLivros()])
    const c = await listarLivros()

    expect(fetchFalso).toHaveBeenCalledTimes(1)
    expect(a).toEqual(b)
    expect(c).toEqual(a)
  })

  it('depois de um erro tenta de novo na proxima chamada', async () => {
    const fetchFalso = vi
      .fn()
      .mockResolvedValueOnce(respostaJson({ detail: 'fora do ar' }, 503))
      .mockResolvedValueOnce(respostaJson([{ livro: 'Genesis' }]))
    vi.stubGlobal('fetch', fetchFalso)

    await expect(listarLivros()).rejects.toBeInstanceOf(ErroApi)
    await expect(listarLivros()).resolves.toEqual([{ livro: 'Genesis' }])
    expect(fetchFalso).toHaveBeenCalledTimes(2)
  })
})
