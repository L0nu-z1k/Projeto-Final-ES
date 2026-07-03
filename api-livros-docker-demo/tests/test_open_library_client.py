from unittest.mock import MagicMock, patch

from open_library_client import OpenLibraryClient, _extrair_ano


def _mock_httpx(payload):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = payload

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_resp
    return mock_client


def test_buscar_isbn_encontrado():
    payload = {
        "ISBN:0132350882": {
            "title": "Clean Code",
            "authors": [{"name": "Robert C. Martin"}],
            "publish_date": "2008",
        }
    }

    with patch("open_library_client.httpx.Client", return_value=_mock_httpx(payload)):
        resultado = OpenLibraryClient().buscar_por_isbn("0132350882")

    assert resultado.titulo == "Clean Code"
    assert resultado.autor == "Robert C. Martin"
    assert resultado.ano == 2008


def test_buscar_isbn_nao_encontrado():
    with patch("open_library_client.httpx.Client", return_value=_mock_httpx({})):
        assert OpenLibraryClient().buscar_por_isbn("0000000000") is None


def test_buscar_isbn_sem_titulo_ou_autor():
    payload = {
        "ISBN:0132350882": {
            "title": "",
            "authors": [],
            "publish_date": "2008",
        }
    }

    with patch("open_library_client.httpx.Client", return_value=_mock_httpx(payload)):
        assert OpenLibraryClient().buscar_por_isbn("0132350882") is None


def test_extrair_ano():
    assert _extrair_ano("August 2008") == 2008
    assert _extrair_ano(None) is None
