from datetime import datetime

from exceptions import AnoInvalidoError, IsbnDuplicadoError, IsbnNaoEncontradoError
from models import Livro, LivroAtualizar, LivroCriar
from open_library_client import DadosOpenLibrary, OpenLibraryClient
from repository import RepositorioLivros


class ServicoLivros:
    def __init__(self, repositorio: RepositorioLivros, open_library: OpenLibraryClient):
        self._repo = repositorio
        self._open_library = open_library

    def listar(self) -> list[Livro]:
        return self._repo.listar()

    def buscar(self, livro_id: int) -> Livro | None:
        return self._repo.buscar_por_id(livro_id)

    def criar(self, dados: LivroCriar) -> Livro:
        if self._repo.buscar_por_isbn(dados.isbn):
            raise IsbnDuplicadoError(f"ISBN {dados.isbn} ja cadastrado")

        meta = self._open_library.buscar_por_isbn(dados.isbn)
        if meta is None:
            raise IsbnNaoEncontradoError(f"ISBN {dados.isbn} nao encontrado")

        self._validar_ano(dados.ano, meta)

        return self._repo.adicionar(LivroCriar(
            titulo=meta.titulo,
            autor=meta.autor,
            ano=dados.ano,
            isbn=dados.isbn,
        ))

    def atualizar(self, livro_id: int, dados: LivroAtualizar) -> Livro | None:
        if not self._repo.buscar_por_id(livro_id):
            return None

        outro = self._repo.buscar_por_isbn(dados.isbn)
        if outro and outro.id != livro_id:
            raise IsbnDuplicadoError(f"ISBN {dados.isbn} ja cadastrado")

        self._validar_ano(dados.ano, None)
        return self._repo.atualizar(livro_id, dados)

    def remover(self, livro_id: int) -> bool:
        return self._repo.remover(livro_id)

    def _validar_ano(self, ano: int, meta: DadosOpenLibrary | None) -> None:
        if ano > datetime.now().year:
            raise AnoInvalidoError(f"Ano {ano} nao pode ser futuro")

        if meta and meta.ano and abs(ano - meta.ano) > 2:
            raise AnoInvalidoError(
                f"Ano {ano} diverge da Open Library ({meta.ano})"
            )
