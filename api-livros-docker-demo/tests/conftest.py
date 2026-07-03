"""Fixtures (configurações reutilizáveis) para os testes.

Este módulo fornece mocks e configurações compartilhadas entre os testes.
"""
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from main import criar_app, criar_servico
from open_library_client import DadosOpenLibrary, OpenLibraryClient
from repository import RepositorioEmMemoria
from service import ServicoLivros


@pytest.fixture
def metadados_open_library():
    """Cria dados padrão da OpenLibrary para testes.
    
    Returns:
        DadosOpenLibrary com dados do livro 'Clean Code'
    """
    return DadosOpenLibrary(
        titulo="Clean Code",
        autor="Robert C. Martin",
        ano=2008,
    )


@pytest.fixture
def mock_open_library(metadados_open_library):
    """Mock do cliente OpenLibrary que retorna dados padrão.
    
    Args:
        metadados_open_library: Dados padrão para retornar
        
    Returns:
        Mock do OpenLibraryClient
    """
    cliente = MagicMock(spec=OpenLibraryClient)
    cliente.buscar_por_isbn.return_value = metadados_open_library
    return cliente


@pytest.fixture
def repositorio():
    """Cria um repositório em memória vazio para testes.
    
    Returns:
        RepositorioEmMemoria inicializado
    """
    return RepositorioEmMemoria()


@pytest.fixture
def servico(repositorio, mock_open_library):
    """Cria um serviço com repositório e mock da OpenLibrary.
    
    Args:
        repositorio: Repositório em memória
        mock_open_library: Mock do cliente OpenLibrary
        
    Returns:
        ServicoLivros configurado para testes
    """
    return criar_servico(repositorio=repositorio, open_library=mock_open_library)


@pytest.fixture
def client(servico):
    """Cria um cliente de teste para a API.
    
    Args:
        servico: Serviço de livros configurado
        
    Returns:
        TestClient para fazer requisições à API
    """
    return TestClient(criar_app(servico=servico))
