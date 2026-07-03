from models import LivroAtualizar, LivroCriar
from repository import RepositorioEmMemoria


def test_adicionar_e_listar():
    repo = RepositorioEmMemoria()
    livro = repo.adicionar(LivroCriar(titulo="A", autor="B", ano=2008, isbn="111"))

    assert len(repo.listar()) == 1
    assert livro.id == 1


def test_buscar_por_isbn():
    repo = RepositorioEmMemoria()
    repo.adicionar(LivroCriar(titulo="A", autor="B", ano=2008, isbn="222"))

    assert repo.buscar_por_isbn("222") is not None
    assert repo.buscar_por_isbn("999") is None


def test_atualizar_e_remover():
    repo = RepositorioEmMemoria()
    livro = repo.adicionar(LivroCriar(titulo="A", autor="B", ano=2008, isbn="333"))

    atualizado = repo.atualizar(
        livro.id,
        LivroAtualizar(titulo="Novo", autor="Autor", ano=2009, isbn="333"),
    )
    assert atualizado.titulo == "Novo"
    assert repo.remover(livro.id) is True
    assert repo.remover(livro.id) is False
