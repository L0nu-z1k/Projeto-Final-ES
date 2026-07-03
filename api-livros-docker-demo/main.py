from fastapi import FastAPI, HTTPException, status

from exceptions import AnoInvalidoError, IsbnDuplicadoError, IsbnNaoEncontradoError
from models import Livro, LivroAtualizar, LivroCriar
from open_library_client import OpenLibraryClient
from repository import RepositorioEmMemoria, RepositorioLivros
from service import ServicoLivros


def criar_servico(
    repositorio: RepositorioLivros | None = None,
    open_library: OpenLibraryClient | None = None,
) -> ServicoLivros:
    return ServicoLivros(
        repositorio=repositorio or RepositorioEmMemoria(),
        open_library=open_library or OpenLibraryClient(),
    )


def criar_app(servico: ServicoLivros | None = None) -> FastAPI:
    api = FastAPI(title="Catalogo de Livros", version="1.1.0")
    svc = servico or criar_servico()

    @api.get("/livros", response_model=list[Livro])
    def listar_livros():
        return svc.listar()

    @api.get("/livros/{livro_id}", response_model=Livro)
    def buscar_livro(livro_id: int):
        livro = svc.buscar(livro_id)
        if livro is None:
            raise HTTPException(status_code=404, detail="Livro nao encontrado")
        return livro

    @api.post("/livros", response_model=Livro, status_code=status.HTTP_201_CREATED)
    def criar_livro(dados: LivroCriar):
        try:
            return svc.criar(dados)
        except IsbnDuplicadoError as e:
            raise HTTPException(status_code=409, detail=str(e)) from e
        except (IsbnNaoEncontradoError, AnoInvalidoError) as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

    @api.put("/livros/{livro_id}", response_model=Livro)
    def atualizar_livro(livro_id: int, dados: LivroAtualizar):
        try:
            livro = svc.atualizar(livro_id, dados)
        except IsbnDuplicadoError as e:
            raise HTTPException(status_code=409, detail=str(e)) from e
        except AnoInvalidoError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

        if livro is None:
            raise HTTPException(status_code=404, detail="Livro nao encontrado")
        return livro

    @api.delete("/livros/{livro_id}", status_code=status.HTTP_200_OK)
    def remover_livro(livro_id: int):
        if not svc.remover(livro_id):
            raise HTTPException(status_code=404, detail="Livro nao encontrado")
        return {"mensagem": "Livro removido com sucesso"}

    return api


app = criar_app()
