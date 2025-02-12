from typing import Any, Dict, List
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import transaction_parser


@pytest.fixture
def sample_transactions() -> list:
    return [
        {"Дата операции": "31.12.2021 15:44:39", "Номер карты": "*7197", "Статус": "OK", "Сумма операции": -78.05},
        {"Дата операции": "26.12.2021 16:30:13", "Номер карты": "*7197", "Статус": "OK", "Сумма операции": -34.0},
    ]


@patch("pandas.read_excel")
def test_transaction_parser_xlsx(mock_read_excel: Any, sample_transactions: List[Dict]) -> None:
    """Тест загрузки XLSX-файла."""
    df_mock = pd.DataFrame(sample_transactions)
    mock_read_excel.return_value = df_mock

    transactions = transaction_parser("data/transactions.xlsx")
    assert transactions == sample_transactions
    mock_read_excel.assert_called_once_with("data/transactions.xlsx")


def test_transaction_parser_unsupported_format() -> None:
    """Тест ошибки при неподдерживаемом формате файла."""
    transactions = transaction_parser("data/transactions.csv")
    assert transactions == []


def test_transaction_parser_file_not_found() -> None:
    """Тест ошибки при отсутствии файла."""
    with patch("pandas.read_excel", side_effect=FileNotFoundError):
        transactions = transaction_parser("data/missing.xlsx")
        assert transactions == []


def test_transaction_parser_empty_file() -> None:
    """Тест ошибки при пустом файле."""
    with patch("pandas.read_excel", side_effect=pd.errors.EmptyDataError):
        transactions = transaction_parser("data/empty.xlsx")
        assert transactions == []
