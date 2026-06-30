import pytest
import httpx
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

# --- TESTES DE UNIDADE E MOCKS (Item 3.3 do PDF) ---

def test_criar_livro_com_enriquecimento_mock():
    """Testa se o sistema busca o autor no Mock quando enviamos um espaço."""
    novo_livro = {
        "titulo": "Livro Teste",
        "autor": " ",  # Espaço para passar no Pydantic e disparar a lógica do service
        "ano": 2020,
        "isbn": "9788535914849"
    }

    with patch("httpx.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "ISBN:9788535914849": {
                    "title": "Livro Teste",
                    "authors": [{"name": "Autor da API Externa"}]
                }
            }
        )

        response = client.post("/livros", json=novo_livro)
        assert response.status_code == 201
        assert response.json()["autor"] == "Autor da API Externa"

def test_open_library_falha_silenciosa():
    """Testa se o sistema sobrevive a um erro de rede (Item 3.3)."""
    novo_livro = {"titulo": "T", "autor": "A", "ano": 2022, "isbn": "err-500"}
    
    with patch("httpx.get") as mock_get:
        # Simulando um erro específico do httpx (como o service espera)
        mock_get.side_effect = httpx.RequestError("Erro de Rede", request=None)
        
        response = client.post("/livros", json=novo_livro)
        assert response.status_code == 201 

def test_erro_isbn_duplicado():
    livro = {"titulo": "Original", "autor": "Autor", "ano": 2021, "isbn": "dup-1"}
    client.post("/livros", json=livro)
    response = client.post("/livros", json=livro)
    assert response.status_code == 409

def test_erro_ano_invalido():
    livro = {"titulo": "V", "autor": "A", "ano": 900, "isbn": "isbn-900"}
    response = client.post("/livros", json=livro)
    assert response.status_code == 422

# --- TESTES DE INTEGRAÇÃO (Item 3.2 do PDF) ---

def test_fluxo_completo_livro():
    """Testa listagem, busca e atualização."""
    # 1. Cria
    livro_data = {"titulo": "Bio", "autor": "N", "ano": 2010, "isbn": "isbn-integ"}
    post_res = client.post("/livros", json=livro_data)
    id_livro = post_res.json()["id"]

    # 2. Busca por ID
    get_res = client.get(f"/livros/{id_livro}")
    assert get_res.status_code == 200

    # 3. Atualiza
    put_res = client.put(f"/livros/{id_livro}", json=livro_data)
    assert put_res.status_code == 200

def test_remover_livro_sucesso_e_erro():
    res = client.post("/livros", json={"titulo": "T", "autor": "A", "ano": 2000, "isbn": "del-123"})
    id_livro = res.json()["id"]
    assert client.delete(f"/livros/{id_livro}").status_code == 200
    assert client.delete(f"/livros/{id_livro}").status_code == 404