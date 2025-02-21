from typing import Dict, List

import pandas as pd
import pytest


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    """Создаёт объединённый DataFrame с тестовыми транзакциями."""
    data = {
        "Дата операции": [
            "11.02.2024 10:30:00",
            "10.02.2024 12:45:00",
            "09.02.2024 18:00:00",
            "31.01.2024 22:00:00",
            "25.12.2023 14:15:00",
            "10.02.2024 14:00:00",  # Для top_transactions
            "09.02.2024 13:00:00",
            "08.02.2024 16:30:00",
            "07.02.2024 10:15:00",
            "06.02.2024 20:00:00",
            "05.02.2024 11:45:00",
        ],
        "Сумма операции": [-500, -200, -300, -150, -50, -1500, -1200, -900, -500, -400, -300],
        "Категория": [
            "Еда",
            "Кафе",
            "Транспорт",
            "Развлечения",
            "Магазины",
            "Еда",
            "Развлечения",
            "Транспорт",
            "Магазины",
            "Кафе",
            "Подписки",
        ],
        "Описание": [
            "Ресторан",
            "Кофейня",
            "Такси",
            "Кино",
            "Магазин",
            "Ресторан",
            "Кино",
            "Такси",
            "Покупка в магазине",
            "Кофейня",
            "Netflix",
        ],
        "Статус": ["OK"] * 11,
        "Номер карты": ["*7197", "*7197", "*1234", "*5678", None, "*7197", "*7197", "*1234", "*5678", None, "*0000"],
    }

    return pd.DataFrame(data)


@pytest.fixture
def sample_transactions_df() -> pd.DataFrame:
    """Тестовый DataFrame с транзакциями"""
    return pd.DataFrame(
        {
            "Дата операции": ["15.12.2021 10:30:00", "10.11.2021 14:00:00", "05.12.2021 18:45:00"],
            "Категория": ["Переводы", "Продукты", "Переводы"],
            "Сумма": [5000, 1500, 2000],
        }
    )


@pytest.fixture
def sample_transactions_cashback() -> List[Dict]:
    return [
        {"Дата операции": "15.01.2024 12:30:00", "Категория": "Продукты", "Сумма операции": -1530},
        {"Дата операции": "18.01.2024 14:00:00", "Категория": "Кафе", "Сумма операции": -810},
        {"Дата операции": "25.01.2024 10:15:00", "Категория": "Продукты", "Сумма операции": -2270},
        {"Дата операции": "02.02.2024 16:45:00", "Категория": "Транспорт", "Сумма операции": -590},
        {"Дата операции": "10.01.2024 08:30:00", "Категория": "Неизвестно", "Сумма операции": "Ошибка"},
    ]


@pytest.fixture
def sample_transactions_searching() -> List[Dict]:
    return [
        {
            "Дата операции": "15.01.2024 12:30:00",
            "Описание": "Оплата в кафе",
            "Категория": "Кафе",
            "Сумма операции": -500,
        },
        {
            "Дата операции": "18.01.2024 14:00:00",
            "Описание": "Перевод Иванов И.",
            "Категория": "Переводы",
            "Сумма операции": -2000,
        },
        {
            "Дата операции": "25.01.2024 10:15:00",
            "Описание": "Магазин продуктов",
            "Категория": "Продукты",
            "Сумма операции": -1500,
        },
        {
            "Дата операции": "10.02.2024 09:45:00",
            "Описание": "Перевод Петров П.",
            "Категория": "Переводы",
            "Сумма операции": -3000,
        },
        {
            "Дата операции": "05.02.2024 16:20:00",
            "Описание": "Пополнение мобильного +7 923 456-78-90",
            "Категория": "Связь",
            "Сумма операции": -500,
        },
    ]
