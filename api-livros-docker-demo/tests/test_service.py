import pytest

from exceptions import AnoInvalidoError, IsbnDuplicadoError, IsbnNaoEncontradoError
from models import LivroAtualizar, LivroCriar
from open_library_client import DadosOpenLibrary


def test_criar_usa_dados_da_open_library(servico, mock_open_library):
    livro = servico.criar(LivroCriar(
        titulo="x", autor="y", ano=2008, isbn="0132350882",
    ))

    assert livro.titulo == "Clean Code"
    assert livro.autor == "Robert C. Martin"
    mock_open_library.buscar_por_isbn.assert_called_once_with("0132350882")


def test_criar_recusa_isbn_duplicado(servico, mock_open_library):
    dados = LivroCriar(titulo="A", autor="B", ano=2008, isbn="0132350882")
    servico.criar(dados)

    with pytest.raises(IsbnDuplicadoError):
        servico.criar(dados)

    assert mock_open_library.buscar_por_isbn.call_count == 1


def test_criar_recusa_isbn_inexistente(servico, mock_open_library):
    mock_open_library.buscar_por_isbn.return_value = None

    with pytest.raises(IsbnNaoEncontradoError):
        servico.criar(LivroCriar(titulo="A", autor="B", ano=2008, isbn="0000000000"))


def test_criar_recusa_ano_futuro(servico):
    with pytest.raises(AnoInvalidoError):
        servico.criar(LivroCriar(titulo="A", autor="B", ano=2099, isbn="0132350882"))


def test_criar_recusa_ano_divergente(servico, mock_open_library):
    mock_open_library.buscar_por_isbn.return_value = DadosOpenLibrary(
        titulo="Clean Code", autor="Robert C. Martin", ano=2008,
    )

    with pytest.raises(AnoInvalidoError):
        servico.criar(LivroCriar(titulo="A", autor="B", ano=1990, isbn="0132350882"))


def test_atualizar_recusa_isbn_de_outro_livro(servico, mock_open_library):
    mock_open_library.buscar_por_isbn.side_effect = [
        DadosOpenLibrary(titulo="Clean Code", autor="Robert C. Martin", ano=2008),
        DadosOpenLibrary(titulo="Design Patterns", autor="Erich Gamma", ano=1994),
    ]
    primeiro = servico.criar(LivroCriar(titulo="A", autor="B", ano=2008, isbn="0132350882"))
    segundo = servico.criar(LivroCriar(titulo="A", autor="B", ano=1994, isbn="0201633612"))

    with pytest.raises(IsbnDuplicadoError):
        servico.atualizar(segundo.id, LivroAtualizar(
            titulo="Outro", autor="Autor", ano=1994, isbn=primeiro.isbn,
        ))


def test_atualizar_recusa_ano_futuro(servico, mock_open_library):
    livro = servico.criar(LivroCriar(titulo="A", autor="B", ano=2008, isbn="0132350882"))

    with pytest.raises(AnoInvalidoError):
        servico.atualizar(livro.id, LivroAtualizar(
            titulo="A", autor="B", ano=2099, isbn="0132350882",
        ))


def test_atualizar_id_inexistente(servico):
    assert servico.atualizar(999, LivroAtualizar(
        titulo="A", autor="B", ano=2008, isbn="0132350882",
    )) is None


def test_remover_id_inexistente(servico):
    assert servico.remover(999) is False
