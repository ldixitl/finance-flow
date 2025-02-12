import json
import logging
import os

from src.external_api import currency_exchanger, stock_exchanger
from src.utils import transaction_parser
from src.views import cost_analysis, filter_transactions_by_month, get_greeting, get_top_transactions

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


def main(current_datetime: str, transactions_path: str = "data/operations.xlsx") -> str:
    """
    Главная функция для работы приложения.
    :param current_datetime:
    :param transactions_path:
    :return:
    """
    try:
        logger.info("Начало работы приложения.")

        try:
            with open("user_settings.json") as file:
                user_settings = json.load(file)
            logger.info("Файл 'user_settings.json' успешно загружен.")
        except FileNotFoundError:
            logger.warning("Файл 'user_settings.json' не найден. Используются настройки по умолчанию.")
            user_settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["INTC", "NVDA"]}

        user_currencies = user_settings.get("user_currencies", [])
        user_stocks = user_settings.get("user_stocks", [])

        # Загрузка и фильтрация транзакций
        transactions = transaction_parser(transactions_path)
        logger.info("Транзакции успешно загружены.")

        monthly_transactions = filter_transactions_by_month(transactions, current_datetime)
        logger.info("Транзакции успешно отфильтрованы за текущий месяц.")

        # Анализ расходов по картам
        card_spends = cost_analysis(monthly_transactions)
        logger.info("Расходы по картам успешно подсчитаны.")

        # Составление топа транзакций
        top_transactions = get_top_transactions(monthly_transactions)
        logger.info("Топ транзакций успешно составлен.")

        # Получение курсов валют и акций
        currency_rates = currency_exchanger(user_currencies)
        logger.info("Курсы валют успешно получены.")

        stock_rates = stock_exchanger(user_stocks)
        logger.info("Курсы акций успешно получены.")

        # Формирование JSON-ответа
        response = {
            "greeting": get_greeting(current_datetime),
            "cards": card_spends,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_rates": stock_rates,
        }
        result = json.dumps(response, ensure_ascii=False, indent=4)
        logger.info("JSON-ответ успешно сформирован.")
        return result

    except Exception as e:
        logger.error(f"Произошла ошибка при работе программы: {e}.", exc_info=True)
        return json.dumps({"error": "Произошла ошибка при обработке запроса."}, ensure_ascii=False, indent=4)
    finally:
        logger.info("Завершение работы программы.")


if __name__ == "__main__":
    print(main("2020-09-29 22:38:50"))
