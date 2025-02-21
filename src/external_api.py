import os
from typing import Dict, List

import requests
from dotenv import load_dotenv

from src.logger_config import add_logger

# Загрузка переменных окружения
load_dotenv()
API_KEY_CURRENCY = os.getenv("API_KEY_CURRENCY")
URL_CURRENCY = "https://api.apilayer.com/exchangerates_data/convert"
API_KEY_STOCK = os.getenv("API_KEY_STOCK")
URL_STOCK = "http://api.marketstack.com/v1/eod/latest"

# Настройка логирования
logger = add_logger("e_api.log", "e_api")


def currency_exchanger(currencies_list: List) -> List[Dict]:
    """
    Функция для получения курса валют к рублю.
    :param currencies_list: Список кодов валют.
    :return: Список словарей с данными о курсе валют.
    """
    logger.info(f"Вызов функции 'currency_exchanger' с параметром '{currencies_list}'.")

    if not API_KEY_CURRENCY:
        logger.error("API_KEY_CURRENCY не задан.")
        return []

    currencies_rates = []
    for currency in currencies_list:

        payload = {"to": "RUB", "from": currency, "amount": 1}
        headers = {"apikey": API_KEY_CURRENCY}

        try:
            response = requests.get(URL_CURRENCY, headers=headers, params=payload)
            response.raise_for_status()
            data = response.json()

            if "result" in data:
                rate = round(data["result"], 2)
                currencies_rates.append({"currency": currency, "rate": rate})
                logger.info(f"Курс '{currency}' -> RUB: {rate}.")
            else:
                logger.warning(f"Ключ 'result' отсутствует в ответе API для {currency}.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе курса {currency}: {e}.", exc_info=True)
            return []
        except KeyError as e:
            logger.error(f"Ошибка обработки ответа API для {currency}: {e}.", exc_info=True)
            return []

    if not currencies_rates:
        logger.warning("Не удалось получить ни одного курса валют.")
        return []

    logger.info(f"Количество валют о которых получена информация: {len(currencies_rates)}.")
    return currencies_rates


def stock_exchanger(stocks_list: List) -> List[Dict]:
    """
    Функция для получения цен на акции.
    :param stocks_list: Список тикеров акций.
    :return: Список словарей с ценами акций в долларах.
    """
    logger.info(f"Вызов функции 'stock_exchanger' с параметром '{stocks_list}'.")

    if not API_KEY_STOCK:
        logger.error("API_KEY_STOCK не задан.")
        return []

    stocks_rates = []
    for stock in stocks_list:
        params = {"access_key": API_KEY_STOCK, "symbols": stock}
        try:
            response = requests.get(url=URL_STOCK, params=params)
            response.raise_for_status()
            data = response.json()

            if "data" not in data or not isinstance(data["data"], list) or not data["data"]:
                logger.warning(f"Данные по акции '{stock}' не найдены.")
                continue

            rate = data["data"][0]["close"]
            stocks_rates.append({"stock": stock, "price": rate})
            logger.info(f"Курс '{stock}' -> USD: {rate}.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе API для '{stock}': {e}.", exc_info=True)
        except (KeyError, IndexError) as e:
            logger.error(f"Ошибка в структуре ответа API для '{stock}': {e}.", exc_info=True)

    if not stocks_rates:
        logger.warning("Не удалось получить ни одного курса акций.")
        return []

    logger.info(f"Количество акций о которых получена информация: {len(stocks_rates)}.")
    return stocks_rates
