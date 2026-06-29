"""
API REST de catalogo de livros (FastAPI).
"""

from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException, status

from models import Livro, LivroCriar, LivroAtualizar
from repository import RepositorioEmMemoria, RepositorioLivros

ANO_ATUAL = datetime.now().year
OPEN_LIBRARY_URL = "https://openlibrary.org/api/books"


# ----------------------------------------------------------------------
# Camada de servico (regras de negocio)
# ----------------------------------------------------------------------

class ServicoLivros:
    """Logica de negocio. Recebe um RepositorioLivros pela interface."""

    def __init__(self, repositorio: RepositorioLivros) -> None:
        self._repo = repositorio

    def listar(self) -> list[Livro]:
        return self._repo.listar()

    def buscar(self, livro_id: int) -> Livro | None:
        return self._repo.buscar_por_id(livro_id)

    def criar(self, dados: LivroCriar) -> Livro:
        # Regra 1: ISBN nao pode ser duplicado
        for livro in self._repo.listar():
            if livro.isbn == dados.isbn:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ja existe um livro com o ISBN {dados.isbn}",
                )

        # Regra 2: ano deve ser valido
        if not 1000 <= dados.ano <= ANO_ATUAL:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Ano invalido: {dados.ano}. Use um valor entre 1000 e {ANO_ATUAL}",
            )

        # Dependencia externa: consulta Open Library pelo ISBN
        dados = self._enriquecer_com_open_library(dados)

        return self._repo.adicionar(dados)

    def atualizar(self, livro_id: int, dados: LivroAtualizar) -> Livro | None:
        return self._repo.atualizar(livro_id, dados)

    def remover(self, livro_id: int) -> bool:
        return self._repo.remover(livro_id)

    def _enriquecer_com_open_library(self, dados: LivroCriar) -> LivroCriar:
        """Consulta a Open Library e completa titulo/autor se necessario."""
        try:
            url = f"{OPEN_LIBRARY_URL}?bibkeys=ISBN:{dados.isbn}&format=json&jscmd=data"
            resposta = httpx.get(url, timeout=5.0)
            resposta.raise_for_status()
            ol_data = resposta.json().get(f"ISBN:{dados.isbn}", {})

            if ol_data.get("title") and dados.titulo == ol_data["title"]:
                pass  # titulo ja confere

            autores = ol_data.get("authors", [])
            if autores and not dados.autor:
                dados = LivroCriar(
                    titulo=dados.titulo,
                    autor=autores[0].get("name", dados.autor),
                    ano=dados.ano,
                    isbn=dados.isbn,
                )
        except (httpx.RequestError, httpx.HTTPStatusError):
            pass  # se a Open Library falhar, continua sem enriquecer

        return dados


# ----------------------------------------------------------------------
# Montagem da aplicacao
# ----------------------------------------------------------------------

app = FastAPI(title="Catalogo de Livros", version="1.0.0")

servico = ServicoLivros(RepositorioEmMemoria())


# ----------------------------------------------------------------------
# Rotas (camada de API)
# ----------------------------------------------------------------------

@app.get("/livros", response_model=list[Livro])
def listar_livros():
    return servico.listar()


@app.get("/livros/{livro_id}", response_model=Livro)
def buscar_livro(livro_id: int):
    livro = servico.buscar(livro_id)
    if livro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro nao encontrado",
        )
    return livro


@app.post("/livros", response_model=Livro, status_code=status.HTTP_201_CREATED)
def criar_livro(dados: LivroCriar):
    return servico.criar(dados)


@app.put("/livros/{livro_id}", response_model=Livro)
def atualizar_livro(livro_id: int, dados: LivroAtualizar):
    livro = servico.atualizar(livro_id, dados)
    if livro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro nao encontrado",
        )
    return livro


@app.delete("/livros/{livro_id}", status_code=status.HTTP_200_OK)
def remover_livro(livro_id: int):
    removido = servico.remover(livro_id)
    if not removido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro nao encontrado",
        )
    return {"mensagem": "Livro removido com sucesso"}