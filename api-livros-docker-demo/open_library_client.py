from dataclasses import dataclass

import httpx

OPEN_LIBRARY_URL = "https://openlibrary.org/api/books"


@dataclass(frozen=True)
class DadosOpenLibrary:
    titulo: str
    autor: str
    ano: int | None


class OpenLibraryClient:
    def __init__(self, base_url: str = OPEN_LIBRARY_URL, timeout: float = 10.0):
        self._base_url = base_url
        self._timeout = timeout

    def buscar_por_isbn(self, isbn: str) -> DadosOpenLibrary | None:
        chave = f"ISBN:{isbn}"
        params = {"bibkeys": chave, "format": "json", "jscmd": "data"}

        with httpx.Client(timeout=self._timeout) as client:
            resp = client.get(self._base_url, params=params)
            resp.raise_for_status()
            payload = resp.json()

        livro = payload.get(chave)
        if not livro:
            return None

        titulo = livro.get("title", "")
        autores = livro.get("authors", [])
        autor = autores[0].get("name", "") if autores else ""

        if not titulo or not autor:
            return None

        return DadosOpenLibrary(
            titulo=titulo,
            autor=autor,
            ano=_extrair_ano(livro.get("publish_date")),
        )


def _extrair_ano(publish_date: str | None) -> int | None:
    if not publish_date:
        return None
    for parte in str(publish_date).split():
        if parte.isdigit() and len(parte) == 4:
            return int(parte)
    return None
