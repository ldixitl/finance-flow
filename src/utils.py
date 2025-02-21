from datetime import datetime
from typing import Dict, List, Union

import pandas as pd

from src.logger_config import add_logger

# Настройка логирования
logger = add_logger("utils.log", "utils")


def transaction_parser(file_path: str, as_dataframe: bool = True) -> Union[List[Dict], pd.DataFrame]:
    """
    Функция для загрузки списка транзакций из файла 'XLSX' формата. При возникновении ошибки возвращает пустой список.
    :param file_path: Путь до файла с транзакциями в формате 'XLSX'.
    :param as_dataframe: Если True, возвращает DataFrame, иначе список словарей.
    :return: DataFrame или List[Dict] с транзакциями.
    """
    try:
        logger.info(f"Вызов функции 'transaction_parser' с параметром '{file_path}'")
        if file_path.endswith("xlsx"):
            transactions = pd.read_excel(file_path)
        else:
            logger.error(f"Неподдерживаемый формат файла '{file_path}'")
            return []

        logger.info(f"Файл '{file_path}' успешно загружен. Найдено {len(transactions)} операций")

        if as_dataframe:
            return transactions
        else:
            return transactions.to_dict(orient="records")

    except FileNotFoundError:
        logger.error(f"Файл по пути '{file_path}' не найден", exc_info=True)
        return []
    except pd.errors.EmptyDataError:
        logger.warning(f"Файл '{file_path}' пустой.", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"Произошла ошибка при обработке файла '{file_path}': {e}", exc_info=True)
        return []


def get_greeting() -> str:
    """
    Функция подбирает необходимое приветствие в соответствии с текущим временем суток.
    :return: Строка с приветствием.
    """
    try:
        current_hour = datetime.now().hour
        logger.info(f"Определение приветствия. Текущее время: {current_hour}:00")

        if 6 <= current_hour < 12:
            greeting = "Доброе утро"
        elif 12 <= current_hour < 18:
            greeting = "Добрый день"
        elif 18 <= current_hour < 23:
            greeting = "Добрый вечер"
        else:
            greeting = "Доброй ночи"

        logger.info(f"Определено приветствие: '{greeting}'.")
        return greeting

    except Exception as e:
        logger.error(f"Ошибка при определении приветствия: {e}.", exc_info=True)
        return "Ошибка: невозможно определить время"


def filter_transactions_by_month(transactions: pd.DataFrame, current_date: str) -> pd.DataFrame:
    """
    Отфильтровывает транзакции, совершённые с начала месяца по текущую дату.
    :param transactions: DataFrame с данными о транзакциях.
                        Столбец "Дата операции" должен содержать дату в формате '%d.%m.%Y %H:%M:%S'.
    :param current_date: Строка с текущей датой в формате ISO-8601.
    :return: Отфильтрованный DataFrame с транзакциями за текущий месяц. В случае ошибки возвращает пустой DataFrame.
    """
    logger.info(
        f"""Вызов функции 'filter_transactions_by_month' с параметром '{current_date}'.
Количество полученных транзакций: {len(transactions)}."""
    )
    today_date = pd.to_datetime(current_date).date()
    start_date = today_date.replace(day=1)

    try:
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

        filtered_transactions = transactions[
            (transactions["Дата операции"].dt.date >= start_date)
            & (transactions["Дата операции"].dt.date <= today_date)
        ]

        logger.info(f"Количество транзакций после фильтрации: {len(filtered_transactions)}.")
        return filtered_transactions

    except Exception as e:
        logger.error(f"Ошибка при фильтрации транзакций: {e}.", exc_info=True)
        return pd.DataFrame()


def cost_analysis(transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Функция группирует траты по картам.
    :param transactions: DataFrame с данными о транзакциях.
    :return: DataFrame с информацией о картах. В случае ошибки возвращает пустой DataFrame.
    """
    logger.info(f"Вызов функции 'cost_analysis'. Количество полученных транзакций: {len(transactions)}.")
    try:
        transactions["Сумма операции"] = pd.to_numeric(transactions["Сумма операции"], errors="coerce").fillna(0)
        transactions["Номер карты"] = transactions["Номер карты"].astype(str)

        spending_transactions = transactions[transactions["Сумма операции"] < 0].copy()
        spending_transactions["last_digits"] = spending_transactions["Номер карты"].fillna("N/A").astype(str).str[-4:]

        card_summary = spending_transactions.groupby("last_digits", as_index=False)["Сумма операции"].sum()
        card_summary["Сумма операции"] = card_summary["Сумма операции"].abs()
        card_summary["cashback"] = card_summary["Сумма операции"] * 0.01

        result = card_summary.rename(columns={"Сумма операции": "total_spent"})

        logger.info(f"Обработано карт: {len(result)}.")
        return result

    except Exception as e:
        logger.error(f"Ошибка при анализе расходов по картам: {e}.", exc_info=True)
        return pd.DataFrame()


def get_top_transactions(transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Функция для подсчёта 5-ти самых затратных транзакций.
    :param transactions: DataFrame с данными о транзакциях.
    :return: DataFrame с данными о 5-ти самых затратных транзакциях. В случае ошибки возвращает пустой DataFrame.
    """
    logger.info(f"Вызов функции 'get_top_transactions'. Количество полученных транзакций: {len(transactions)}.")
    try:
        transactions["Сумма операции"] = pd.to_numeric(transactions["Сумма операции"], errors="coerce").fillna(0)

        spending_transactions = transactions[
            (transactions["Сумма операции"] < 0) & (transactions["Статус"].str.upper() != "FAILED")
        ]

        if spending_transactions.empty:
            logger.warning("Не найдено ни одной подходящей операции.")
            return pd.DataFrame()

        top_5_transactions = spending_transactions.nsmallest(5, "Сумма операции")

        result = top_5_transactions[["Дата операции", "Сумма операции", "Категория", "Описание"]].copy()

        result["Дата операции"] = result["Дата операции"].fillna("N/A")
        result["Сумма операции"] = result["Сумма операции"].fillna(0)
        result["Категория"] = result["Категория"].fillna("Неизвестно")
        result["Описание"] = result["Описание"].fillna("Без описания")

        result.rename(
            columns={
                "Дата операции": "date",
                "Сумма операции": "amount",
                "Категория": "category",
                "Описание": "description",
            },
            inplace=True,
        )

        logger.info(f"Топ-5 транзакций успешно сформирован. Количество: {len(result)}.")
        return result

    except Exception as e:
        logger.error(f"Ошибка в 'get_top_transactions': {e}.", exc_info=True)
        return pd.DataFrame()
