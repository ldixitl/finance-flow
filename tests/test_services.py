import json
import logging

from src.services import (
    cashback_analysis,
    find_personal_transfer,
    find_phone_numbers,
    investment_bank,
    searching_transactions,
)


def test_cashback_analysis(sample_transactions_cashback, caplog) -> None:
    """Тест со смешанными данными, где есть верные и ошибочные данные."""
    caplog.set_level(logging.DEBUG)

    result = cashback_analysis(sample_transactions_cashback, 2024, 1)
    cashback_data = json.loads(result)

    assert cashback_data == {"Продукты": 38.0, "Кафе": 8.1}

    assert "Вызов функции 'cashback_analysis'" in caplog.text
    assert "Кэшбэк по категориям сформирован" in caplog.text
    assert "Произошла ошибка при обработке транзакции" in caplog.text


def test_investment_bank(sample_transactions_cashback, caplog) -> None:
    """Тест со смешанными данными, где есть верные и ошибочные данные."""
    caplog.set_level(logging.INFO)

    saved_amount = investment_bank(sample_transactions_cashback, "2024-01", 100)
    assert saved_amount == 190

    assert "Вызов функции 'investment_bank'" in caplog.text
    assert "По транзакции '0' отложено в копилку" in caplog.text
    assert "Произошла ошибка при обработке транзакции" in caplog.text
    assert "Общая сумма, накопленная в 'Инвесткопилке'" in caplog.text


def test_searching_transactions(sample_transactions_searching, caplog) -> None:
    """Тест функции поиска транзакций по ключевому слову."""
    caplog.set_level(logging.INFO)

    result = searching_transactions(sample_transactions_searching, "кафе")
    transactions = json.loads(result)

    assert len(transactions) == 1

    assert "Вызов функции 'searching_transactions'" in caplog.text
    assert "Найдено 1 транзакций по запросу 'кафе'." in caplog.text


def test_find_phone_numbers(sample_transactions_searching, caplog) -> None:
    """Тест функции поиска транзакций с номерами телефонов."""
    caplog.set_level(logging.INFO)

    result = find_phone_numbers(sample_transactions_searching)
    transactions = json.loads(result)

    assert len(transactions) == 1

    assert "Вызов функции 'find_phone_numbers'" in caplog.text
    assert "Найдено 1 транзакций с номерами телефонов." in caplog.text


def test_find_personal_transfer(sample_transactions_searching, caplog) -> None:
    """Тест функции поиска транзакций, связанных с переводами физическим лицам."""
    caplog.set_level(logging.INFO)

    result = find_personal_transfer(sample_transactions_searching)
    transactions = json.loads(result)

    assert len(transactions) == 2

    assert "Вызов функции 'find_personal_transfer'" in caplog.text
    assert "Найдено 2 транзакций с номерами телефонов." in caplog.text
