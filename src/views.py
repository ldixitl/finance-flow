import logging
from datetime import datetime
from typing import Dict, List

from dateutil import parser

# Настройка логирования
logger = logging.getLogger("views")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("logs/views.log", mode="w", encoding="UTF-8")
file_formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(levelname)s: %(message)s", datefmt="%d-%m-%Y %H:%M:%S"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_greeting(current_date: str) -> str:
    """
    Функция подбирает необходимое приветствие в соответствии с текущим временем суток.
    :param current_date: Строка с текущей датой в формате ISO-8601.
    :return: Строка с приветствием.
    """
    try:
        logger.info(f"Вызов функции 'get_greeting' с параметром '{current_date}'.")
        hour = parser.isoparse(current_date).hour
        if 12 > hour >= 6:
            logger.info("Определено приветствие: 'Доброе утро'.")
            return "Доброе утро"
        elif 18 > hour >= 12:
            logger.info("Определено приветствие: 'Добрый день'.")
            return "Добрый день"
        elif 6 > hour >= 0:
            logger.info("Определено приветствие: 'Доброй ночи'.")
            return "Доброй ночи"
        else:
            logger.info("Определено приветствие: 'Добрый вечер'.")
            return "Добрый вечер"

    except (TypeError, ValueError) as e:
        logger.error(f"Ошибка обработки даты: {e}.", exc_info=True)
        return "Ошибка: некорректная дата"


def filter_transactions_by_month(transaction_list: List[Dict], current_date: str) -> List[Dict]:
    """
    Отфильтровывает транзакции, совершённые с начала месяца по текущую дату.
    :param transaction_list: Список словарей с данными о транзакциях.
                            Ключ "Дата операции" должен содержать дату в формате '%d.%m.%Y'.
    :param current_date: Строка с текущей датой в формате ISO-8601.
    :return: Отфильтрованный список словарей с транзакциями за текущий месяц.
    """
    logger.info(
        f"""Вызов функции 'filter_transactions_by_month' с параметром '{current_date}'.
Количество полученных транзакций: {len(transaction_list)}."""
    )
    today_date = parser.parse(current_date).date()
    start_date = today_date.replace(day=1)

    filtered_transactions = []
    for transaction in transaction_list:
        transaction_date_str = transaction.get("Дата операции")

        if not isinstance(transaction_date_str, str):
            logger.error(
                f"""Некорректный тип данных в дате (id={transaction_list.index(transaction) + 1}).
Ожидается строка, получено {type(transaction_date_str)}."""
            )
            continue

        try:
            transaction_date = datetime.strptime(transaction_date_str.split()[0], "%d.%m.%Y").date()
        except ValueError:
            logger.error(
                f"Ошибка парсинга даты (id={transaction_list.index(transaction) + 1}): '{transaction_date_str}'"
            )
            continue

        if today_date >= transaction_date >= start_date:
            filtered_transactions.append(transaction)

    logger.info(f"Количество транзакций после фильтрации: {len(filtered_transactions)}")
    return filtered_transactions


def cost_analysis(transaction_list: List[Dict]) -> List[Dict]:
    """
    Функция группирует траты по картам.
    :param transaction_list: Список словарей с данными о транзакциях.
    :return: Список словарей с информацией о картах.
    """
    logger.info(f"Вызов функции 'cost_analysis'. Количество полученных транзакций: '{len(transaction_list)}'.")
    card_summary = {}

    for transaction in transaction_list:
        card_number = transaction.get("Номер карты")
        amount = transaction.get("Сумма операции")

        if not isinstance(amount, (float, int, str)):
            logger.warning(f"Некорректный тип данных суммы: {amount}. ID = {transaction_list.index(transaction) + 1})")
            continue

        try:
            amount_float = float(amount)
        except ValueError:
            logger.warning(
                f"Ошибка при конвертации: {amount}. ID = {transaction_list.index(transaction) + 1})", exc_info=True
            )
            continue

        if amount_float >= 0:
            logger.info(f"Транзакция не является расходом. ID = {transaction_list.index(transaction) + 1})")
            continue

        if isinstance(card_number, str):
            last_digits = card_number[-4:]
        else:
            last_digits = "N/A"

        if last_digits not in card_summary:
            card_summary[last_digits] = 0.0

        logger.info(f"Карта {last_digits}: добавлен расход {abs(amount_float)}")
        card_summary[last_digits] += abs(amount_float)

    card_list = []
    for card, spent in card_summary.items():
        card_list.append({"last_digits": card, "total_spent": round(spent, 2), "cashback": round(spent * 0.01, 2)})

    logger.info(f"Обработано карт: {len(card_list)}.")
    return card_list
