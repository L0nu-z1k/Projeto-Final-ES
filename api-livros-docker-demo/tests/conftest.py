from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from main import criar_app, criar_servico
from open_library_client import DadosOpenLibrary, OpenLibraryClient
from repository import RepositorioEmMemoria
from service import ServicoLivros


@pytest.fixture
def metadados_open_library():
    return DadosOpenLibrary(
        titulo="Clean Code",
        autor="Robert C. Martin",
        ano=2008,
    )


@pytest.fixture
def mock_open_library(metadados_open_library):
    cliente = MagicMock(spec=OpenLibraryClient)
    cliente.buscar_por_isbn.return_value = metadados_open_library
    return cliente


@pytest.fixture
def repositorio():
    return RepositorioEmMemoria()


@pytest.fixture
def servico(repositorio, mock_open_library):
    return criar_servico(repositorio=repositorio, open_library=mock_open_library)


@pytest.fixture
def client(servico):
    return TestClient(criar_app(servico=servico))
