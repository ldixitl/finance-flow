from typing import Dict, List, Union

import pytest

from src.views import cost_analysis, filter_transactions_by_month, get_greeting, get_top_transactions


@pytest.mark.parametrize(
    "current_date, expected_greeting",
    [
        ("2024-02-11T07:00:00", "Доброе утро"),
        ("2024-02-11T13:00:00", "Добрый день"),
        ("2024-02-11T19:00:00", "Добрый вечер"),
        ("2024-02-11T03:00:00", "Доброй ночи"),
    ],
)
def test_get_greeting(current_date: str, expected_greeting: str) -> None:
    """Тестирование выбора корректного приветствия в зависимости от времени суток."""
    assert get_greeting(current_date) == expected_greeting


@pytest.mark.parametrize(
    "invalid_date",
    [None, "", "invalid_date", "2024-13-40T25:61:00"],
)
def test_get_greeting_invalid_date(invalid_date: Union[None, str]) -> None:
    """Тестирование обработки некорректной даты."""
    assert get_greeting(invalid_date) == "Ошибка: некорректная дата"


def test_filter_transactions_by_month(sample_transactions: List[Dict]) -> None:
    """Тестирование фильтрации транзакций за текущий месяц."""
    filtered = filter_transactions_by_month(sample_transactions, "2024-02-11T12:00:00")
    assert len(filtered) == 4  # Ожидаем транзакции от 10.02, 09.02, 11.02


def test_filter_transactions_by_month_empty() -> None:
    """Тестирование фильтрации, если транзакций нет."""
    assert filter_transactions_by_month([], "2024-02-11T12:00:00") == []


def test_filter_transactions_by_month_invalid_date_format() -> None:
    """Тестирование обработки некорректного формата даты."""
    transactions = [{"Дата операции": "неправильная дата", "Сумма операции": 100}]
    assert filter_transactions_by_month(transactions, "2024-02-11T12:00:00") == []


def test_filter_transactions_by_month_missing_date_key() -> None:
    """Тестирование случая, когда у транзакции нет ключа 'Дата операции'."""
    transactions = [{"Сумма операции": 100}]
    assert filter_transactions_by_month(transactions, "2024-02-11T12:00:00") == []


def test_filter_transactions_by_month_wrong_type() -> None:
    """Тестирование случая, когда 'Дата операции' не строка."""
    transactions = [{"Дата операции": 123456, "Сумма операции": 100}]
    assert filter_transactions_by_month(transactions, "2024-02-11T12:00:00") == []


def test_cost_analysis(sample_transactions: List[Dict]) -> None:
    """Тест группировки трат по картам."""
    result = cost_analysis(sample_transactions)

    assert len(result) == 4  # 3 карты с расходами и одна None
    assert result[0]["last_digits"] == "7197"
    assert result[0]["total_spent"] == 2000  # 500 + 1500
    assert result[0]["cashback"] == 20.0
    assert result[1]["last_digits"] == "1234"
    assert result[1]["total_spent"] == 200  # Только одна расходная транзакция
    assert result[2]["last_digits"] == "5678"
    assert result[2]["total_spent"] == 100  # Учтена строка "-100", пропущена "abc"


def test_cost_analysis_empty() -> None:
    """Тест обработки пустого списка."""
    assert cost_analysis([]) == []


def test_cost_analysis_no_expenses() -> None:
    """Тест, если нет расходных транзакций."""
    transactions = [
        {"Номер карты": "1234567890123456", "Сумма операции": 1000},
        {"Номер карты": "9876543210987654", "Сумма операции": 2000},
    ]
    assert cost_analysis(transactions) == []


def test_get_top_transactions(sample_top_transactions: List[Dict]) -> None:
    """Тест получения топ-5 затратных операций."""
    result = get_top_transactions(sample_top_transactions)

    assert len(result) == 5  # Должно быть 5 транзакций
    assert result[0]["amount"] == -1500  # Самая затратная
    assert result[1]["amount"] == -1200
    assert result[2]["amount"] == -900
    assert result[3]["amount"] == -500
    assert result[4]["amount"] == -400  # Пятая по величине


def test_get_top_transactions_empty() -> None:
    """Тест, если передан пустой список."""
    assert get_top_transactions([]) == []


def test_get_top_transactions_no_expenses() -> None:
    """Тест, если нет расходных операций."""
    transactions = [
        {"Дата операции": "10.02.2024", "Сумма операции": 500, "Категория": "Доход", "Описание": "Перевод"},
    ]
    assert get_top_transactions(transactions) == []


def test_get_top_transactions_failed_status() -> None:
    """Тест, если операции имеют статус 'FAILED'."""
    transactions = [
        {
            "Дата операции": "10.02.2024",
            "Сумма операции": -500,
            "Категория": "Еда",
            "Описание": "Ресторан",
            "Статус": "FAILED",
        },
        {
            "Дата операции": "12.02.2024",
            "Сумма операции": -1500,
            "Категория": "Развлечения",
            "Описание": "Кино",
            "Статус": "FAILED",
        },
    ]
    assert get_top_transactions(transactions) == []
