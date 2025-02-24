import json
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from src.logger_config import add_logger

# Настройка логирования
logger = add_logger("services.log", "services")

PHONE_PATTERN = re.compile(r"\+7\s\d{3}\s\d{3}[-\s]?\d{2}[-\s]?\d{2}")
NAME_PATTERN = re.compile(r"\b[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.")


def cashback_analysis(transaction_list: List[Dict], year: int, month: int) -> str:
    """
    Анализирует список транзакций на наиболее подходящие категории кэшбэка.
    :param transaction_list: Список словарей с данными о транзакциях.
    :param year: Год, за который проводится анализ.
    :param month: Месяц за который проводится анализ.
    :return: JSON с анализом возможного заработка кэшбэка по категориям.
    """
    logger.info(
        f"""Вызов функции 'cashback_analysis' с параметрами: год - {year}, месяц - {month}.
Количество полученных транзакций: {len(transaction_list)}."""
    )

    cashback_categories = defaultdict(float)
    for i, transaction in enumerate(transaction_list):
        try:
            transaction_date = datetime.strptime(transaction.get("Дата операции").split()[0], "%d.%m.%Y")
            if (
                transaction_date.year == year
                and transaction_date.month == month
                and transaction.get("Сумма операции") < 0
            ):
                category = transaction.get("Категория", "Неизвестно")
                amount = abs(transaction.get("Сумма операции"))
                cashback_categories[category] += amount * 0.01

        except (TypeError, KeyError, ValueError) as e:
            logger.warning(f"Произошла ошибка при обработке транзакции (ID={i}): {e}.", exc_info=True)
            continue

    cashback_categories = {category: round(total, 2) for category, total in cashback_categories.items()}
    logger.info(f"Кэшбэк по категориям сформирован. Количество категорий: {len(cashback_categories)}")
    return json.dumps(cashback_categories, indent=4, ensure_ascii=False)


def investment_bank(transaction_list: List[Dict], month: str, limit: int) -> float:
    """
    Рассчитывает сумму, которая могла бы быть отложена в «Инвесткопилку» за указанный месяц.
    :param transaction_list: Список словарей с данными о транзакциях.
    :param month: Строка в формате 'YYYY-MM'.
    :param limit: Лимит для округления.
    :return: Возможная отложенная сумма.
    """
    logger.info(
        f"""Вызов функции 'investment_bank' с параметрами: месяц - {month}, лимит - {limit}.
Количество полученных транзакций: {len(transaction_list)}."""
    )
    total_saved = 0.0
    for i, transaction in enumerate(transaction_list):
        try:
            transaction_date = datetime.strptime(transaction.get("Дата операции").split()[0], "%d.%m.%Y")
            if transaction_date.strftime("%Y-%m") != month:
                continue

            if transaction.get("Сумма операции") < 0:
                amount = abs(transaction.get("Сумма операции"))
                if amount % limit != 0:
                    amount_rounded = (amount // limit + 1) * limit
                    total_saved += amount_rounded - amount
                    logger.info(f"По транзакции '{i}' отложено в копилку: {amount_rounded - amount}")

        except (TypeError, KeyError, ValueError) as e:
            logger.warning(f"Произошла ошибка при обработке транзакции (ID={i}): {e}.", exc_info=True)
            continue

    logger.info(f"Общая сумма, накопленная в 'Инвесткопилке' за {month}: {total_saved} ₽.")
    return round(total_saved, 2)


def searching_transactions(transaction_list: List[Dict], query: str) -> str:
    """
    Осуществляет поиск транзакций, которые содержат запрос в описании или категории.
    :param transaction_list: Список словарей с данными о транзакциях.
    :param query: Строка для запроса пользователем.
    :return: JSON-ответ со всеми транзакциями, содержащими запрос в описании или категории.
    """
    logger.info(
        f"""Вызов функции 'searching_transactions' с параметром: {query}.
Количество полученных транзакций: {len(transaction_list)}."""
    )
    query = query.lower()

    found_transactions = []
    for i, transaction in enumerate(transaction_list):
        try:
            if (
                query in str(transaction.get("Описание", "")).lower()
                or query in str(transaction.get("Категория", "")).lower()
            ):
                found_transactions.append(transaction)
        except (TypeError, KeyError, ValueError) as e:
            logger.warning(f"Произошла ошибка при обработке транзакции (ID={i}): {e}.", exc_info=True)
            continue

    logger.info(f"Найдено {len(found_transactions)} транзакций по запросу '{query}'.")
    return json.dumps(found_transactions, indent=4, ensure_ascii=False)


def find_phone_numbers(transaction_list: List[Dict]) -> str:
    """
    Осуществляет поиск транзакций, которые содержат номер телефона в описании.
    :param transaction_list: Список словарей с данными о транзакциях.
    :return: JSON-ответ со всеми транзакциями, содержащими номер телефона в описании.
    """
    logger.info(f"Вызов функции 'find_phone_numbers'. Количество полученных транзакций: {len(transaction_list)}.")

    found_transactions = []
    for i, transaction in enumerate(transaction_list):
        try:
            if PHONE_PATTERN.search(str(transaction.get("Описание", ""))):
                found_transactions.append(transaction)
        except Exception as e:
            logger.warning(f"Ошибка при обработке транзакции (ID={i}): {e}.", exc_info=True)

    logger.info(f"Найдено {len(found_transactions)} транзакций с номерами телефонов.")
    return json.dumps(found_transactions, indent=4, ensure_ascii=False)


def find_personal_transfer(transaction_list: List[Dict]) -> str:
    """
    Осуществляет поиск транзакций, которые относятся к переводам физическим лицам.
    :param transaction_list: Список словарей с данными о транзакциях.
    :return: JSON-ответ со всеми транзакциями, являющимися переводам физическим лицам.
    """
    logger.info(f"Вызов функции 'find_personal_transfer'. Количество полученных транзакций: {len(transaction_list)}.")

    found_transactions = []
    for i, transaction in enumerate(transaction_list):
        try:
            if transaction.get("Категория", "") == "Переводы" and NAME_PATTERN.search(
                str(transaction.get("Описание", ""))
            ):
                found_transactions.append(transaction)
        except Exception as e:
            logger.warning(f"Ошибка при обработке транзакции (ID={i}): {e}.", exc_info=True)
            continue

    logger.info(f"Найдено {len(found_transactions)} транзакций с номерами телефонов.")
    return json.dumps(found_transactions, indent=4, ensure_ascii=False)
