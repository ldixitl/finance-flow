import json
import os
from datetime import datetime
from functools import wraps
from typing import Optional

import pandas as pd

from src.logger_config import add_logger

# Настройка логирования
logger = add_logger("reports.log", "reports")


def save_to_file(filename: str = None):
    """Декоратор, сохраняющий результат выполнения функции в JSON файл.
    Если имя файла не передано, используется имя по умолчанию."""

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            logger.info(f"Запуск функции '{function.__name__}'.")
            result = function(*args, **kwargs)

            if isinstance(result, pd.DataFrame):
                result_to_save = result.to_dict(orient="records")

            path_project = os.path.dirname(os.path.dirname(__file__))
            path_reports = os.path.join(path_project, "reports_data")
            os.makedirs(path_reports, exist_ok=True)

            if filename:
                report_file = os.path.join(path_reports, filename)
            else:
                default_name = f"report_{function.__name__}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
                report_file = os.path.join(path_reports, default_name)

            try:
                with open(report_file, "w", encoding="utf-8") as file:
                    json.dump(result_to_save, file, indent=4, ensure_ascii=False)
                logger.info(f"Файл успешно сохранён: {report_file}")
            except (OSError, json.JSONDecodeError, TypeError) as e:
                logger.error(f"Ошибка при сохранении отчета в {report_file}: {e}.", exc_info=True)

            return result

        return wrapper

    return decorator


@save_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Вычисляет траты по указанной категории за последние три месяца от указанной даты.
    :param transactions: Датафрейм с данными о транзакциях.
    :param category: Строка с необходимой категорией.
    :param date: Дата отсчёта (опционально).
    :return: Отфильтрованный датафрейм с тратами.
    """
    logger.info(
        f"""Вызов функции 'spending_by_category' с параметрами: category - {category}, date - {date}."
Количество полученных транзакций: {len(transactions)}"""
    )
    try:
        if date:
            start_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            start_date = datetime.today()

        end_date = start_date - pd.DateOffset(months=3)

        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

        filtered_transactions = transactions[
            (transactions["Дата операции"] >= end_date)
            & (transactions["Дата операции"] <= start_date)
            & (transactions["Категория"] == category)
        ]

        logger.info(
            f"Найдено {len(filtered_transactions)} транзакций в категории '{category}' с {end_date} по {start_date}."
        )

        if filtered_transactions.empty:
            logger.warning(f"Нет данных по категории '{category}' за указанный период")

        filtered_transactions["Дата операции"] = filtered_transactions["Дата операции"].astype(str)

        return filtered_transactions
    except Exception as e:
        logger.error(f"Ошибка при обработке транзакций: {e}.", exc_info=True)
        raise
