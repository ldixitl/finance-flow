import logging
import os
from typing import Dict, List

import requests
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
API_KEY_EXCHANGER = os.getenv("API_KEY_EXCHANGER")
URL_EXCHANGER = os.getenv("URL_EXCHANGER")

# Настройка логирования
logger = logging.getLogger("e_api")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("logs/e_api.log", mode="w", encoding="UTF-8")
file_formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(levelname)s: %(message)s", datefmt="%d-%m-%Y %H:%M:%S"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def currency_exchanger(currencies_list: List) -> List[Dict]:
    """
    Функция для получения курса валют к рублю.
    :param currencies_list: Список кодов валют.
    :return: Список словарей с данными о курсе валют.
    """
    logger.info(f"Вызов функции 'currency_exchanger' с параметром '{currencies_list}'")
    if not API_KEY_EXCHANGER:
        logger.error("API_KEY_EXCHANGER is not set.")
        return []

    currencies_rates = []
    for currency in currencies_list:

        payload = {"to": "RUB", "from": currency, "amount": 1}
        headers = {"apikey": API_KEY_EXCHANGER}

        try:
            response = requests.get(URL_EXCHANGER, headers=headers, params=payload)
            response.raise_for_status()
            data = response.json()

            if "result" in data:
                rate = round(data["result"], 2)
                currencies_rates.append({"currency": currency, "rate": rate})
                logger.info(f"Курс {currency} -> RUB: {rate}")
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
