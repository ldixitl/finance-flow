import json
import os

import pandas as pd

from src.external_api import currency_exchanger, stock_exchanger
from src.logger_config import add_logger
from src.utils import (cost_analysis, filter_transactions_by_month, get_greeting, get_top_transactions,
                       transaction_parser)

# Настройка логирования
logger = add_logger("views.log", "views")

path_project = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def convert_timestamps(obj):
    """
    Рекурсивно конвертирует pandas.Timestamp в строки внутри списка или словаря.
    """
    if isinstance(obj, pd.Timestamp):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(obj, list):
        return [convert_timestamps(item) for item in obj]
    if isinstance(obj, dict):
        return {key: convert_timestamps(value) for key, value in obj.items()}
    return obj


def main_view(current_datetime: str, transactions_path: str = None) -> str:
    """
    Главная функция обработки данных и формирования JSON-ответа.
    :param current_datetime: Строка с датой и временем в формате 'YYYY-MM-DD HH:MM:SS'.
    :param transactions_path: Путь до файла с транзакциями.
    :return: JSON-ответ с анализом транзакций, курсами валют и акциями.
    """
    try:
        logger.info("Начало работы приложения.")

        # Определение путей
        settings_path = os.path.join(path_project, "user_settings.json")
        transactions_path = os.path.join(path_project, transactions_path)

        # Загрузка пользовательских настроек
        try:
            with open(settings_path) as file:
                user_settings = json.load(file)
            logger.info("Файл 'user_settings.json' успешно загружен.")
        except FileNotFoundError:
            logger.warning("Файл 'user_settings.json' не найден. Используются настройки по умолчанию.")
            user_settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["INTC", "NVDA"]}

        user_currencies = user_settings.get("user_currencies", [])
        user_stocks = user_settings.get("user_stocks", [])

        # Загрузка транзакций в DataFrame
        transactions = transaction_parser(transactions_path, as_dataframe=True).copy()
        logger.info(f"Транзакции успешно загружены. Размер: {transactions.shape}.")

        # Фильтрация транзакций за текущий месяц
        monthly_transactions = filter_transactions_by_month(transactions, current_datetime).copy()
        logger.info(f"Транзакции успешно отфильтрованы за месяц. Размер: {monthly_transactions.shape}.")

        # Анализ расходов по картам
        card_spends = cost_analysis(monthly_transactions).copy()
        card_spends["last_digits"] = card_spends["last_digits"].fillna("N/A")  # Обработка NaN
        logger.info(f"Расходы по картам успешно подсчитаны. Размер: {card_spends.shape}.")

        # Составление топа транзакций
        top_transactions = get_top_transactions(monthly_transactions).copy()
        logger.info(f"Топ транзакций успешно составлен. Размер: {top_transactions.shape}.")

        # Получение курсов валют и акций
        currency_rates = currency_exchanger(user_currencies)
        logger.info(f"Курсы валют успешно получены. Количество: {len(currency_rates)}.")

        stock_rates = stock_exchanger(user_stocks)
        logger.info(f"Курсы акций успешно получены. Количество: {len(stock_rates)}.")

        # Формирование JSON-ответа с конвертацией Timestamp
        response = {
            "greeting": get_greeting(),
            "cards": card_spends.to_dict(orient="records"),
            "top_transactions": top_transactions.to_dict(orient="records"),
            "currency_rates": currency_rates,
            "stock_rates": stock_rates,
        }
        response = convert_timestamps(response)  # Конвертация Timestamps

        result = json.dumps(response, ensure_ascii=False, indent=4)
        logger.info("JSON-ответ успешно сформирован.")
        return result

    except Exception as e:
        logger.error(f"Произошла ошибка при работе программы: {e}.", exc_info=True)
        return json.dumps({"error": "Произошла ошибка при обработке запроса."}, ensure_ascii=False, indent=4)
    finally:
        logger.info("Завершение работы программы.")


if __name__ == "__main__":
    print(main_view("2020-09-29 22:38:50", "data/operations.xlsx"))
