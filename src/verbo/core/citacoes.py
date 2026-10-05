import re
import unicodedata

from verbo.core.util import separar_referencia

# Nomes dos 73 livros como aparecem no indice (referencia dos versiculos)
LIVROS = [
    "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio", "Josué", "Juízes", "Rute",
    "I Samuel", "II Samuel", "I Reis", "II Reis", "I Crônicas", "II Crônicas", "Esdras",
    "Neemias", "Tobias", "Judite", "Ester", "Jó", "Salmos", "I Macabeus", "II Macabeus",
    "Provérbios", "Eclesiastes", "Cântico dos Cânticos", "Sabedoria", "Eclesiástico",
    "Isaías", "Jeremias", "Lamentações", "Baruc", "Ezequiel", "Daniel", "Oséias", "Joel",
    "Amós", "Abdias", "Jonas", "Miquéias", "Naum", "Habacuc", "Sofonias", "Ageu",
    "Zacarias", "Malaquias", "São Mateus", "São Marcos", "São Lucas", "São João",
    "Atos dos Apóstolos", "Romanos", "I Coríntios", "II Coríntios", "Gálatas", "Efésios",
    "Filipenses", "Colossenses", "I Tessalonicenses", "II Tessalonicenses", "I Timóteo",
    "II Timóteo", "Tito", "Filêmon", "Hebreus", "São Tiago", "I São Pedro", "II São Pedro",
    "I São João", "II São João", "III São João", "São Judas", "Apocalipse",
]

# Outras formas comuns de escrever o nome (ja sem acento e em minusculo)
_VARIANTES = {
    "Atos dos Apóstolos": ["atos"],
    "Cântico dos Cânticos": ["cantares", "cantico dos canticos", "cantico"],
    "Salmos": ["salmo"],
    "Provérbios": ["proverbio"],
    "Eclesiástico": ["siracida", "ben sira"],
    "Sabedoria": ["sabedoria de salomao"],
    "Apocalipse": ["apocalipse de sao joao"],
    "Lamentações": ["lamentacao"],
}

_ROMANOS = {"I": 1, "II": 2, "III": 3}

# Hifens e travessoes de todos os tipos (o LLM usa o hifen nao separavel nas faixas de versiculos)
_TRACOS = re.compile("[" + chr(0x2010) + "-" + chr(0x2015) + chr(0x2212) + "]")


def _sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c)).lower()


def _normalizar(texto: str) -> str:
    return _TRACOS.sub("-", _sem_acento(texto))


def _apelidos(nome: str) -> list[str]:
    """Formas de escrever o livro: com e sem 'Sao', com numero romano ou arabico."""
    partes = nome.split()
    numero = _ROMANOS.get(partes[0])
    resto = partes[1:] if numero else partes
    sem_sao = [p for p in resto if _sem_acento(p) != "sao"]
    saida = set()
    for forma in {" ".join(resto), " ".join(sem_sao)}:
        base = _sem_acento(forma)
        if numero:
            for prefixo in (partes[0].lower(), str(numero), f"{numero}o", f"{numero}a"):
                saida.add(f"{prefixo} {base}")
        else:
            saida.add(base)
    saida.update(_VARIANTES.get(nome, []))
    return sorted(saida)


def _montar_mapa():
    mapa = {}
    for nome in LIVROS:
        for apelido in _apelidos(nome):
            mapa.setdefault(apelido, nome)
    return mapa


_MAPA = _montar_mapa()
_ALTERNATIVAS = "|".join(re.escape(a) for a in _MAPA)
# livro + capitulo; o que vem depois (":2-4", ", 46") nao importa para conferir o capitulo
_PADRAO = re.compile(rf"(?<![a-z0-9])({_ALTERNATIVAS})\s+(\d{{1,3}})(?![a-z0-9])")


def citacoes_na_resposta(texto: str) -> list[tuple[str, int]]:
    """Capitulos citados no texto, na ordem em que aparecem e sem repetir.
    Trechos sem o nome do livro (como '11:5-8' numa lista de referencias) nao sao lidos."""
    encontrados = []
    for achado in _PADRAO.finditer(_normalizar(texto)):
        capitulo = (_MAPA[achado.group(1)], int(achado.group(2)))
        if capitulo not in encontrados:
            encontrados.append(capitulo)
    return encontrados


def nao_confirmadas(texto: str, versiculos: list[dict]) -> list[str]:
    """Citacoes da resposta cujo capitulo nao estava entre os versiculos enviados ao LLM.
    Devolve textos como 'São Mateus 7', prontos para mostrar."""
    enviados = set()
    for v in versiculos:
        capitulo = separar_referencia(v["referencia"])
        if capitulo:
            enviados.add(capitulo)
    return [
        f"{livro} {capitulo}"
        for livro, capitulo in citacoes_na_resposta(texto)
        if (livro, capitulo) not in enviados
    ]
