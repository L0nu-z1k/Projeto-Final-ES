from abc import ABC, abstractmethod

from models import Livro, LivroAtualizar, LivroCriar


class RepositorioLivros(ABC):
    @abstractmethod
    def listar(self) -> list[Livro]: ...

    @abstractmethod
    def buscar_por_id(self, livro_id: int) -> Livro | None: ...

    @abstractmethod
    def buscar_por_isbn(self, isbn: str) -> Livro | None: ...

    @abstractmethod
    def adicionar(self, dados: LivroCriar) -> Livro: ...

    @abstractmethod
    def atualizar(self, livro_id: int, dados: LivroAtualizar) -> Livro | None: ...

    @abstractmethod
    def remover(self, livro_id: int) -> bool: ...


class RepositorioEmMemoria(RepositorioLivros):
    def __init__(self):
        self._livros: dict[int, Livro] = {}
        self._proximo_id = 1

    def listar(self) -> list[Livro]:
        return list(self._livros.values())

    def buscar_por_id(self, livro_id: int) -> Livro | None:
        return self._livros.get(livro_id)

    def buscar_por_isbn(self, isbn: str) -> Livro | None:
        return next((livro for livro in self._livros.values() if livro.isbn == isbn), None)

    def adicionar(self, dados: LivroCriar) -> Livro:
        livro = Livro(
            id=self._proximo_id,
            titulo=dados.titulo,
            autor=dados.autor,
            ano=dados.ano,
            isbn=dados.isbn,
        )
        self._livros[livro.id] = livro
        self._proximo_id += 1
        return livro

    def atualizar(self, livro_id: int, dados: LivroAtualizar) -> Livro | None:
        if livro_id not in self._livros:
            return None
        atualizado = Livro(
            id=livro_id,
            titulo=dados.titulo,
            autor=dados.autor,
            ano=dados.ano,
            isbn=dados.isbn,
        )
        self._livros[livro_id] = atualizado
        return atualizado

    def remover(self, livro_id: int) -> bool:
        if livro_id not in self._livros:
            return False
        del self._livros[livro_id]
        return True
