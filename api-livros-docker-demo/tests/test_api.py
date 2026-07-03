from open_library_client import DadosOpenLibrary

PAYLOAD = {"titulo": "A", "autor": "B", "ano": 2008, "isbn": "0132350882"}


def test_listar_vazio(client):
    assert client.get("/livros").json() == []


def test_criar_e_buscar(client):
    resp = client.post("/livros", json=PAYLOAD)
    assert resp.status_code == 201
    livro = resp.json()
    assert livro["titulo"] == "Clean Code"
    assert livro["autor"] == "Robert C. Martin"
    assert client.get(f"/livros/{livro['id']}").status_code == 200


def test_isbn_duplicado_409(client):
    client.post("/livros", json=PAYLOAD)
    assert client.post("/livros", json=PAYLOAD).status_code == 409


def test_isbn_inexistente_422(client, mock_open_library):
    mock_open_library.buscar_por_isbn.return_value = None
    resp = client.post("/livros", json={**PAYLOAD, "isbn": "0000000000"})
    assert resp.status_code == 422


def test_ano_futuro_422(client):
    resp = client.post("/livros", json={**PAYLOAD, "ano": 2099})
    assert resp.status_code == 422


def test_ano_divergente_422(client):
    resp = client.post("/livros", json={**PAYLOAD, "ano": 1990})
    assert resp.status_code == 422


def test_buscar_404(client):
    assert client.get("/livros/999").status_code == 404


def test_atualizar(client):
    livro_id = client.post("/livros", json=PAYLOAD).json()["id"]
    resp = client.put(f"/livros/{livro_id}", json={
        "titulo": "Novo", "autor": "Autor", "ano": 2008, "isbn": "0132350882",
    })
    assert resp.status_code == 200
    assert resp.json()["titulo"] == "Novo"


def test_atualizar_404(client):
    assert client.put("/livros/999", json=PAYLOAD).status_code == 404


def test_atualizar_ano_futuro_422(client):
    livro_id = client.post("/livros", json=PAYLOAD).json()["id"]
    resp = client.put(f"/livros/{livro_id}", json={**PAYLOAD, "ano": 2099})
    assert resp.status_code == 422


def test_remover(client):
    livro_id = client.post("/livros", json=PAYLOAD).json()["id"]
    assert client.delete(f"/livros/{livro_id}").status_code == 200
    assert client.get(f"/livros/{livro_id}").status_code == 404


def test_remover_404(client):
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
