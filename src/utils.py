import logging
from typing import Dict, List

import pandas as pd

# Настройка логирования
logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("logs/utils.log", mode="w", encoding="UTF-8")
file_formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(levelname)s: %(message)s", datefmt="%d-%m-%Y %H:%M:%S"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def transaction_parser(file_path: str) -> List[Dict]:
    """
    Функция для загрузки списка транзакций из файла 'XLSX' формата. При возникновении ошибки возвращает пустой список.
    :param file_path: Путь до файла с транзакциями в формате 'XLSX'.
    :return: Список словарей с транзакциями.
    """
    try:
        logger.info(f"Вызов функции 'transaction_parser' с параметром '{file_path}'")
        if file_path.endswith("xlsx"):
            dataframe = pd.read_excel(file_path)
        else:
            logger.error(f"Неподдерживаемый формат файла '{file_path}'")
            return []

        transactions = dataframe.to_dict(orient="records")
        logger.info(f"Файл '{file_path}' успешно загружен. Найдено {len(transactions)} операций")
        return transactions

    except FileNotFoundError:
        logger.error(f"Файл по пути '{file_path}' не найден", exc_info=True)
        return []
    except pd.errors.EmptyDataError:
        logger.warning(f"Файл '{file_path}' пустой.", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"Произошла ошибка при обработке файла '{file_path}': {e}", exc_info=True)
        return []
