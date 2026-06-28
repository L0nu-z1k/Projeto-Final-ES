"""Testes de integracao dos endpoints."""
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_listar_livros():
    """GET /livros deve retornar 200."""
    response = client.get("/livros")
    assert response.status_code == 200


def test_criar_livro_endpoint():
    """POST /livros deve retornar 201."""
    dados = {"titulo": "Teste", "autor": "Autor", "ano": 2021, "isbn": "9991"}
    response = client.post("/livros", json=dados)
    assert response.status_code == 201


def test_buscar_livro_inexistente():
    """GET /livros/9999 deve retornar 404."""
    response = client.get("/livros/9999")
    assert response.status_code == 404


def test_criar_e_buscar_livro():
    """Deve criar e depois encontrar o livro."""
    dados = {"titulo": "Busca", "autor": "Autor", "ano": 2022, "isbn": "9992"}
    post = client.post("/livros", json=dados)
    livro_id = post.json()["id"]
    get = client.get(f"/livros/{livro_id}")
    assert get.status_code == 200


def test_remover_livro():
    """Deve remover livro criado."""
    dados = {"titulo": "Remover", "autor": "Autor", "ano": 2023, "isbn": "9993"}
    post = client.post("/livros", json=dados)
    livro_id = post.json()["id"]
    delete = client.delete(f"/livros/{livro_id}")
    assert delete.status_code == 200