from typing import Any, Dict, List
from unittest.mock import patch

import pandas as pd
import pytest

from src.views import (cost_analysis, filter_transactions_by_month, get_greeting, get_top_transactions,
                       transaction_parser)


@pytest.fixture
def sample_transactions_load() -> list:
    return [
        {"Дата операции": "31.12.2021 15:44:39", "Номер карты": "*7197", "Статус": "OK", "Сумма операции": -78.05},
        {"Дата операции": "26.12.2021 16:30:13", "Номер карты": "*7197", "Статус": "OK", "Сумма операции": -34.0},
    ]


@patch("pandas.read_excel")
def test_transaction_parser_xlsx(mock_read_excel: Any, sample_transactions_load: List[Dict]) -> None:
    """Тест загрузки XLSX-файла."""
    df_mock = pd.DataFrame(sample_transactions_load)
    mock_read_excel.return_value = df_mock

    transactions = transaction_parser("data/transactions.xlsx").to_dict(orient="records")  # Приводим к списку словарей
    assert transactions == sample_transactions_load  # Теперь сравнение корректное
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


@pytest.mark.parametrize(
    "mock_hour, expected_greeting",
    [
        (7, "Доброе утро"),
        (13, "Добрый день"),
        (19, "Добрый вечер"),
        (3, "Доброй ночи"),
    ],
)
@patch("src.utils.datetime")
def test_get_greeting(mock_datetime, mock_hour, expected_greeting) -> None:
    """Тестирование выбора корректного приветствия в зависимости от времени суток."""
    mock_datetime.now.return_value.hour = mock_hour
    assert get_greeting() == expected_greeting


@patch("src.utils.datetime")
def test_get_greeting_exception_handling(mock_datetime) -> None:
    """Тест обработки ошибки в `get_greeting`."""
    mock_datetime.now.side_effect = Exception("Ошибка")
    assert get_greeting() == "Ошибка: невозможно определить время"


def test_filter_transactions_by_month(sample_transactions) -> None:
    """Тестирование фильтрации транзакций за текущий месяц."""
    filtered = filter_transactions_by_month(sample_transactions, "2024-02-11T12:00:00")

    assert len(filtered) == 9  # Ожидаем 9 транзакций в феврале
    assert all(filtered["Дата операции"].dt.month == 2)  # Все операции должны быть в феврале


def test_filter_transactions_by_month_empty() -> None:
    """Тестирование фильтрации, если транзакций нет."""
    empty_df = pd.DataFrame(columns=["Дата операции", "Сумма операции"])
    filtered = filter_transactions_by_month(empty_df, "2024-02-11T12:00:00")
    assert filtered.empty


def test_filter_transactions_by_month_invalid_date_format() -> None:
    """Тестирование обработки некорректного формата даты."""
    transactions = pd.DataFrame({"Дата операции": ["неправильная дата"], "Сумма операции": [100]})
    filtered = filter_transactions_by_month(transactions, "2024-02-11T12:00:00")
    assert filtered.empty


def test_filter_transactions_by_month_missing_date_key() -> None:
    """Тестирование случая, когда у транзакции нет ключа 'Дата операции'."""
    transactions = pd.DataFrame({"Сумма операции": [100]})
    filtered = filter_transactions_by_month(transactions, "2024-02-11T12:00:00")
    assert filtered.empty


def test_filter_transactions_by_month_wrong_type() -> None:
    """Тестирование случая, когда 'Дата операции' не строка."""
    transactions = pd.DataFrame({"Дата операции": [123456], "Сумма операции": [100]})
    filtered = filter_transactions_by_month(transactions, "2024-02-11T12:00:00")
    assert filtered.empty


def test_cost_analysis(sample_transactions: pd.DataFrame) -> None:
    """Тест группировки трат по картам."""
    result = cost_analysis(sample_transactions)

    assert len(result) == 5  # Карт 5: *7197, *1234, *5678, *0000, "N/A"
    assert result.loc[result["last_digits"] == "7197", "total_spent"].values[0] == 3400  # 500 + 1500 + 1400
    assert result.loc[result["last_digits"] == "1234", "total_spent"].values[0] == 1200
    assert result.loc[result["last_digits"] == "5678", "total_spent"].values[0] == 650
    assert result.loc[result["last_digits"] == "0000", "total_spent"].values[0] == 300

    # Проверяем, что "N/A" есть в списке карт, прежде чем к нему обращаться
    if "N/A" in result["last_digits"].values:
        assert result.loc[result["last_digits"] == "N/A", "total_spent"].values[0] == 450


def test_cost_analysis_empty() -> None:
    """Тест обработки пустого DataFrame."""
    empty_df = pd.DataFrame(columns=["Номер карты", "Сумма операции"])
    result = cost_analysis(empty_df)
    assert result.empty


def test_cost_analysis_no_expenses() -> None:
    """Тест, если нет расходных транзакций."""
    transactions = pd.DataFrame({"Номер карты": ["*1234", "*5678"], "Сумма операции": [1000, 2000]})  # Только доходы
    result = cost_analysis(transactions)
    assert result.empty


def test_get_top_transactions(sample_transactions: pd.DataFrame) -> None:
    """Тест получения топ-5 затратных операций."""
    result = get_top_transactions(sample_transactions)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 5  # Должно быть 5 транзакций
    assert result.iloc[0]["amount"] == -1500  # Самая затратная
    assert result.iloc[1]["amount"] == -1200
    assert result.iloc[2]["amount"] == -900
    assert result.iloc[3]["amount"] == -500
    assert result.iloc[4]["amount"] == -500


def test_get_top_transactions_empty() -> None:
    """Тест, если передан пустой DataFrame."""
    empty_df = pd.DataFrame(columns=["Дата операции", "Сумма операции", "Категория", "Описание", "Статус"])
    result = get_top_transactions(empty_df)

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_get_top_transactions_no_expenses() -> None:
    """Тест, если нет расходных операций."""
    transactions = pd.DataFrame(
        {
            "Дата операции": ["10.02.2024"],
            "Сумма операции": [500],  # Доход, а не расход
            "Категория": ["Доход"],
            "Описание": ["Перевод"],
            "Статус": ["OK"],
        }
    )
    result = get_top_transactions(transactions)

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_get_top_transactions_failed_status() -> None:
    """Тест, если операции имеют статус 'FAILED'."""
    transactions = pd.DataFrame(
        {
            "Дата операции": ["10.02.2024", "12.02.2024"],
            "Сумма операции": [-500, -1500],
            "Категория": ["Еда", "Развлечения"],
            "Описание": ["Ресторан", "Кино"],
            "Статус": ["FAILED", "FAILED"],  # Операции не должны попасть в результат
        }
    )
    result = get_top_transactions(transactions)

    assert isinstance(result, pd.DataFrame)
    assert result.empty
