"""Testes de integração da API HTTP.

Estes testes validam as rotas HTTP da API usando o cliente de teste.
"""
from open_library_client import DadosOpenLibrary

# Dados padrão para testes
PAYLOAD = {"titulo": "A", "autor": "B", "ano": 2008, "isbn": "0132350882"}


def test_listar_vazio(client):
    """Testa listagem de livros quando o repositório está vazio."""
    assert client.get("/livros").json() == []


def test_criar_e_buscar(client):
    """Testa criação de livro e busca por ID.
    
    Verifica que:
    - Criação retorna 201 Created
    - Título e autor são substituídos pelos da OpenLibrary
    - Busca por ID encontra o livro
    """
    resp = client.post("/livros", json=PAYLOAD)
    assert resp.status_code == 201
    livro = resp.json()
    assert livro["titulo"] == "Clean Code"
    assert livro["autor"] == "Robert C. Martin"
    assert client.get(f"/livros/{livro['id']}").status_code == 200


def test_isbn_duplicado_409(client):
    """Testa que duplicar ISBN retorna 409 Conflict."""
    client.post("/livros", json=PAYLOAD)
    assert client.post("/livros", json=PAYLOAD).status_code == 409


def test_isbn_inexistente_422(client, mock_open_library):
    """Testa que ISBN não encontrado retorna 422 Unprocessable Entity."""
    mock_open_library.buscar_por_isbn.return_value = None
    resp = client.post("/livros", json={**PAYLOAD, "isbn": "0000000000"})
    assert resp.status_code == 422


def test_ano_futuro_422(client):
    """Testa que ano futuro retorna 422 Unprocessable Entity."""
    resp = client.post("/livros", json={**PAYLOAD, "ano": 2099})
    assert resp.status_code == 422


def test_ano_divergente_422(client):
    """Testa que ano muito diferente da OpenLibrary retorna 422."""
    resp = client.post("/livros", json={**PAYLOAD, "ano": 1990})
    assert resp.status_code == 422


def test_buscar_404(client):
    """Testa que buscar ID inexistente retorna 404 Not Found."""
    assert client.get("/livros/999").status_code == 404


def test_atualizar(client):
    """Testa atualização de um livro existente."""
    livro_id = client.post("/livros", json=PAYLOAD).json()["id"]
    resp = client.put(f"/livros/{livro_id}", json={
        "titulo": "Novo", "autor": "Autor", "ano": 2008, "isbn": "0132350882",
    })
    assert resp.status_code == 200
    assert resp.json()["titulo"] == "Novo"


def test_atualizar_404(client):
    """Testa que atualizar ID inexistente retorna 404."""
    assert client.put("/livros/999", json=PAYLOAD).status_code == 404


def test_atualizar_ano_futuro_422(client):
    livro_id = client.post("/livros", json=PAYLOAD).json()["id"]
    resp = client.put(f"/livros/{livro_id}", json={**PAYLOAD, "ano": 2099})
    assert resp.status_code == 422


def test_remover(client):
    """Testa remoção de um livro existente."""
    livro_id = client.post("/livros", json=PAYLOAD).json()["id"]
    assert client.delete(f"/livros/{livro_id}").status_code == 200
    assert client.get(f"/livros/{livro_id}").status_code == 404


def test_remover_404(client):
    """Testa que remover ID inexistente retorna 404."""
    assert client.delete("/livros/999").status_code == 404


def test_atualizar_isbn_duplicado_409(client, mock_open_library):
    mock_open_library.buscar_por_isbn.side_effect = [
        DadosOpenLibrary(titulo="Clean Code", autor="Robert C. Martin", ano=2008),
        DadosOpenLibrary(titulo="Design Patterns", autor="Erich Gamma", ano=1994),
    ]
    primeiro = client.post("/livros", json=PAYLOAD).json()
    segundo = client.post("/livros", json={
        "titulo": "A", "autor": "B", "ano": 1994, "isbn": "0201633612",
    }).json()

    resp = client.put(f"/livros/{segundo['id']}", json={
        "titulo": "X", "autor": "Y", "ano": 1994, "isbn": primeiro["isbn"],
    })
    assert resp.status_code == 409
