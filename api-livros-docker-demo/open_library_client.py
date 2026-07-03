"""Cliente para integração com a API OpenLibrary.

Este módulo fornece funcionalidades para buscar informações de livros
na OpenLibrary usando ISBN como identificador.
"""
from dataclasses import dataclass

import httpx

OPEN_LIBRARY_URL = "https://openlibrary.org/api/books"


@dataclass(frozen=True)
class DadosOpenLibrary:
    """Dados imutáveis de um livro retornados pela OpenLibrary.
    
    Attributes:
        titulo: Título do livro
        autor: Primeiro autor do livro
        ano: Ano de publicação (pode ser None se não encontrado)
    """
    titulo: str
    autor: str
    ano: int | None


class OpenLibraryClient:
    """Cliente HTTP para buscar livros na API da OpenLibrary.
    
    Attributes:
        _base_url: URL base da API OpenLibrary
        _timeout: Timeout padrão para requisições HTTP
    """
    def __init__(self, base_url: str = OPEN_LIBRARY_URL, timeout: float = 10.0):
        """Inicializa o cliente OpenLibrary.
        
        Args:
            base_url: URL base da API (padrão: https://openlibrary.org/api/books)
            timeout: Timeout para requisições em segundos (padrão: 10.0)
        """
        self._base_url = base_url
        self._timeout = timeout

    def buscar_por_isbn(self, isbn: str) -> DadosOpenLibrary | None:
        """Busca informações de um livro pelo ISBN na OpenLibrary.
        
        Args:
            isbn: Código ISBN do livro a buscar
            
        Returns:
            DadosOpenLibrary com título, autor e ano, ou None se não encontrado
        """
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
    """Extrai o ano de um campo de data de publicação.
    
    Procura pela primeira sequência de 4 dígitos que representa um ano válido.
    
    Args:
        publish_date: String contendo a data de publicação (ex: 'August 2008')
        
    Returns:
        Ano extraído como int, ou None se não encontrado
    """
    if not publish_date:
        return None
    for parte in str(publish_date).split():
        if parte.isdigit() and len(parte) == 4:
            return int(parte)
    return None
