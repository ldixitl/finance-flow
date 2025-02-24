import json
import logging
import os

import pandas as pd

from src.reports import spending_by_category
from src.services import (cashback_analysis, find_personal_transfer, find_phone_numbers, investment_bank,
                          searching_transactions)
from src.utils import transaction_parser
from src.views import main_view

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Настройка логирования
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("logs/main.log", mode="w", encoding="UTF-8")
file_formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(levelname)s: %(message)s", datefmt="%d-%m-%Y %H:%M:%S"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def main():
    """
    Главная функция, запускающая все реализованные модули проекта.
    Последовательно вызываются:
    - Веб-страница (main_view)
    - Сервисы (анализ кэшбэка, инвесткопилка, поиск по транзакциям)
    - Отчеты (траты по категории)
    """

    logger.info("Запуск основной программы...")

    # Загружаем транзакции
    transactions = transaction_parser("data/operations.xlsx", False)
    logger.info(f"Загружено {len(transactions)} транзакций.")

    # 1️Веб-страница
    web_response = main_view("2021-12-20 19:18:12", "data/operations.xlsx")
    logger.info("Сформирован JSON-ответ для веб-страницы.")
    print("Веб-страница:")
    print(json.dumps(json.loads(web_response), indent=4, ensure_ascii=False))

    # Сервисы
    print("\nАнализ кэшбэка:")
    cashback_result = cashback_analysis(transactions, 2021, 2)
    print(cashback_result)

    print("\nИнвесткопилка:")
    investment_result = investment_bank(transactions, "2021-02", 50)
    print(f"Сумма накоплений: {investment_result} ₽")

    print("\nПоиск транзакций с 'Ozon.ru':")
    search_result = searching_transactions(transactions, "Ozon.ru")
    print(search_result)

    print("\nПоиск телефонных номеров в транзакциях:")
    phone_result = find_phone_numbers(transactions)
    print(phone_result)

    print("\nПоиск переводов физическим лицам:")
    personal_transfer_result = find_personal_transfer(transactions)
    print(personal_transfer_result)

    # Отчеты
    print("\nОтчет: Траты по категории 'Переводы'")
    transactions_df = pd.read_excel("data/operations.xlsx")
    spending_report = spending_by_category(transactions_df, "Переводы", "2021-12-20")
    print(spending_report)

    logger.info("Выполнение основной программы завершено.")


if __name__ == "__main__":
    main()
