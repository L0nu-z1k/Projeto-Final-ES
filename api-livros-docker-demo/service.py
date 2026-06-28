"""Servico de negocios para livros com integracao Open Library."""
import requests
from models import Livro, LivroCriar
from repository import RepositorioLivros


class ServicoLivrosExtendido:
    """Servico com regras de negocio e dependencia externa."""

    def __init__(self, repositorio: RepositorioLivros) -> None:
        self._repo = repositorio

    def criar_com_validacao(self, dados: LivroCriar) -> Livro:
        """Cria livro validando ISBN duplicado e consultando Open Library."""
        # Regra 1: ISBN duplicado
        existentes = self._repo.listar()
        for livro in existentes:
            if livro.isbn == dados.isbn:
                raise ValueError(f"ISBN {dados.isbn} ja cadastrado.")

        # Regra 2: Ano invalido
        if dados.ano < 1000 or dados.ano > 2100:
            raise ValueError("Ano invalido.")

        # Dependencia externa: Open Library
        ol_dados = self._buscar_open_library(dados.isbn)
        if ol_dados:
            titulo_ol = ol_dados.get("title")
            autores_ol = ol_dados.get("authors", [])
            autor_ol = autores_ol[0].get("name") if autores_ol else None
            dados = LivroCriar(
                titulo=dados.titulo or titulo_ol or dados.titulo,
                autor=dados.autor or autor_ol or dados.autor,
                ano=dados.ano,
                isbn=dados.isbn,
            )

        return self._repo.adicionar(dados)

    def _buscar_open_library(self, isbn: str):
        """Consulta a Open Library pelo ISBN."""
        url = (
            f"https://openlibrary.org/api/books"
            f"?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        )
        try:
            resposta = requests.get(url, timeout=5)
            dados = resposta.json()
            return dados.get(f"ISBN:{isbn}")
        except Exception:  # pylint: disable=broad-except
            return None