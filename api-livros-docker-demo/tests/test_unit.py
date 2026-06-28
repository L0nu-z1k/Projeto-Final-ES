"""Testes unitarios do servico de livros."""
from unittest.mock import patch
import pytest
from models import LivroCriar
from repository import RepositorioEmMemoria
from service import ServicoLivrosExtendido


def make_servico():
    """Cria servico com repositorio limpo."""
    return ServicoLivrosExtendido(RepositorioEmMemoria())


def make_dados(**kwargs):
    """Cria LivroCriar com valores padrao."""
    defaults = {"titulo": "Livro Teste", "autor": "Autor", "ano": 2020, "isbn": "1111"}
    defaults.update(kwargs)
    return LivroCriar(**defaults)


def test_criar_livro_sucesso():
    """Deve criar livro com sucesso."""
    servico = make_servico()
    with patch.object(servico, "_buscar_open_library", return_value=None):
        livro = servico.criar_com_validacao(make_dados())
    assert livro.isbn == "1111"


def test_isbn_duplicado():
    """Deve recusar ISBN duplicado."""
    servico = make_servico()
    with patch.object(servico, "_buscar_open_library", return_value=None):
        servico.criar_com_validacao(make_dados(isbn="2222"))
        with pytest.raises(ValueError, match="ja cadastrado"):
            servico.criar_com_validacao(make_dados(isbn="2222"))


def test_ano_invalido():
    """Deve recusar ano invalido."""
    servico = make_servico()
    with patch.object(servico, "_buscar_open_library", return_value=None):
        with pytest.raises(ValueError, match="Ano invalido"):
            servico.criar_com_validacao(make_dados(ano=500))


def test_open_library_preenche_titulo():
    """Deve usar titulo da Open Library quando nao informado."""
    servico = make_servico()
    ol_mock = {"title": "Titulo OL", "authors": [{"name": "Autor OL"}]}
    with patch.object(servico, "_buscar_open_library", return_value=ol_mock):
        livro = servico.criar_com_validacao(make_dados(isbn="3333", titulo="X"))
    assert livro.titulo == "X"


def test_listar_vazio():
    """Repositorio novo deve estar vazio."""
    repo = RepositorioEmMemoria()
    assert repo.listar() == []