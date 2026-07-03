"""Serviço de negócio para gerenciar livros.

Este módulo implementa a lógica de negócio para operações com livros,
incluindo validações, integração com OpenLibrary e acesso ao repositório.
"""
from datetime import datetime

from exceptions import AnoInvalidoError, IsbnDuplicadoError, IsbnNaoEncontradoError
from models import Livro, LivroAtualizar, LivroCriar
from open_library_client import DadosOpenLibrary, OpenLibraryClient
from repository import RepositorioLivros


class ServicoLivros:
    """Serviço que gerencia operações de livros com validações de negócio.
    
    Attributes:
        _repo: Repositório para persistência de livros
        _open_library: Cliente para buscar dados na OpenLibrary
    """
    def __init__(self, repositorio: RepositorioLivros, open_library: OpenLibraryClient):
        """Inicializa o serviço de livros.
        
        Args:
            repositorio: Implementação do repositório de livros
            open_library: Cliente para API da OpenLibrary
        """
        self._repo = repositorio
        self._open_library = open_library

    def listar(self) -> list[Livro]:
        """Lista todos os livros cadastrados.
        
        Returns:
            Lista de todos os livros
        """
        return self._repo.listar()

    def buscar(self, livro_id: int) -> Livro | None:
        """Busca um livro pelo ID.
        
        Args:
            livro_id: ID do livro a buscar
            
        Returns:
            Livro encontrado ou None se não existir
        """
        return self._repo.buscar_por_id(livro_id)

    def criar(self, dados: LivroCriar) -> Livro:
        """Cria um novo livro após validações.
        
        Validações:
        - ISBN não pode estar duplicado
        - ISBN deve existir na OpenLibrary
        - Ano não pode ser futuro
        - Ano não deve divergir muito da OpenLibrary
        
        Args:
            dados: Dados do livro a criar
            
        Returns:
            Livro criado com ID atribuído
            
        Raises:
            IsbnDuplicadoError: Se ISBN já existe
            IsbnNaoEncontradoError: Se ISBN não existe na OpenLibrary
            AnoInvalidoError: Se ano é inválido
        """
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
        """Atualiza um livro existente.
        
        Validações similares à criação, mas permite manter o mesmo ISBN.
        
        Args:
            livro_id: ID do livro a atualizar
            dados: Novos dados do livro
            
        Returns:
            Livro atualizado ou None se não encontrado
            
        Raises:
            IsbnDuplicadoError: Se novo ISBN pertence a outro livro
            AnoInvalidoError: Se ano é inválido
        """
        if not self._repo.buscar_por_id(livro_id):
            return None

        outro = self._repo.buscar_por_isbn(dados.isbn)
        if outro and outro.id != livro_id:
            raise IsbnDuplicadoError(f"ISBN {dados.isbn} ja cadastrado")

        self._validar_ano(dados.ano, None)
        return self._repo.atualizar(livro_id, dados)

    def remover(self, livro_id: int) -> bool:
        """Remove um livro do catálogo.
        
        Args:
            livro_id: ID do livro a remover
            
        Returns:
            True se removido com sucesso, False se não encontrado
        """
        return self._repo.remover(livro_id)

    def _validar_ano(self, ano: int, meta: DadosOpenLibrary | None) -> None:
        """Valida se o ano de publicação é válido.
        
        Verifica:
        - Ano não pode ser futuro
        - Ano não deve divergir mais de 2 anos da OpenLibrary (se disponível)
        
        Args:
            ano: Ano a validar
            meta: Dados da OpenLibrary para comparação (opcional)
            
        Raises:
            AnoInvalidoError: Se validação falhar
        """
        if ano > datetime.now().year:
            raise AnoInvalidoError(f"Ano {ano} nao pode ser futuro")

        if meta and meta.ano and abs(ano - meta.ano) > 2:
            raise AnoInvalidoError(
                f"Ano {ano} diverge da Open Library ({meta.ano})"
            )
