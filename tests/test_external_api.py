from unittest.mock import patch

import requests

from src.external_api import currency_exchanger, stock_exchanger


@patch("src.external_api.requests.get")
def test_currency_exchanger_success(mock_get) -> None:
    """Тест успешного получения курса валют"""
    mock_response = {"result": 73.21}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    result = currency_exchanger(["USD"])
    assert result == [{"currency": "USD", "rate": 73.21}]
    mock_get.assert_called_once()


@patch("src.external_api.requests.get")
def test_currency_exchanger_api_failure(mock_get) -> None:
    """Тест обработки ошибки API"""
    mock_get.side_effect = requests.exceptions.RequestException("API Error")

    result = currency_exchanger(["USD"])
    assert result == []


@patch("src.external_api.requests.get")
def test_currency_exchanger_no_api_key(mock_get) -> None:
    """Тест обработки отсутствия API ключа"""
    with patch("src.external_api.API_KEY_CURRENCY", None):
        result = currency_exchanger(["USD"])
        assert result == []
    mock_get.assert_not_called()


@patch("src.external_api.requests.get")
def test_stock_exchanger_success(mock_get) -> None:
    """Тест успешного получения цены акций"""
    mock_response = {"data": [{"close": 150.12}]}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    result = stock_exchanger(["AAPL"])
    assert result == [{"stock": "AAPL", "price": 150.12}]
    mock_get.assert_called_once()


@patch("src.external_api.requests.get")
def test_stock_exchanger_api_failure(mock_get) -> None:
    """Тест обработки ошибки API"""
    mock_get.side_effect = requests.exceptions.RequestException("API Error")

    result = stock_exchanger(["AAPL"])
    assert result == []


def test_stock_exchanger_no_api_key() -> None:
    """Тест обработки отсутствия API ключа"""
    with patch("src.external_api.API_KEY_STOCK", None):
        result = stock_exchanger(["AAPL"])
        assert result == []
