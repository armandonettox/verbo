from verbo.core.leitura import carregar_capitulos_estruturados
from verbo.core.plano_livre import listar_livros
from verbo.core.versiculo_dia import carregar_versiculos_do_arquivo


class Biblia:
    """Texto da Biblia carregado uma vez na memoria quando a API sobe."""

    def __init__(self, caminho):
        self.capitulos = carregar_capitulos_estruturados(caminho)
        self.versiculos = carregar_versiculos_do_arquivo(caminho)
        self.livros = listar_livros(self.capitulos)
        self._indice = {
            (c["livro"], c["capitulo"]): c for c in self.capitulos
        }
        self._total_por_livro = {l["livro"]: l["total_capitulos"] for l in self.livros}

    def obter_capitulo(self, livro, numero):
        capitulo = self._indice.get((livro, numero))
        if capitulo is None:
            return None
        return {**capitulo, "total_capitulos_livro": self._total_por_livro[livro]}
