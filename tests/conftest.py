from typing import Dict, List

import pytest


@pytest.fixture
def sample_transactions() -> List[Dict]:
    """Пример списка транзакций в новом формате."""
    return [
        {"Дата операции": "10.02.2024 12:10:15", "Номер карты": "*7197", "Статус": "OK", "Сумма операции": -500},
        {"Дата операции": "12.01.2024 08:45:50", "Номер карты": "*7197", "Статус": "OK", "Сумма операции": -1500},
        {"Дата операции": "29.01.2024 09:30:10", "Номер карты": "*1234", "Статус": "OK", "Сумма операции": -200},
        {
            "Дата операции": "09.02.2024 07:25:10",
            "Номер карты": "*1234",
            "Статус": "OK",
            "Сумма операции": 300,
        },  # Доход
        {
            "Дата операции": "27.01.2024 18:45:50",
            "Номер карты": "*5678",
            "Статус": "OK",
            "Сумма операции": "-100",
        },  # Строка
        {
            "Дата операции": "11.02.2024 19:00:05",
            "Номер карты": "*5678",
            "Статус": "OK",
            "Сумма операции": "abc",
        },  # Ошибка
        {
            "Дата операции": "10.02.2024 11:55:25",
            "Номер карты": None,
            "Статус": "OK",
            "Сумма операции": -400,
        },  # Без номера карты
    ]


@pytest.fixture
def sample_top_transactions() -> List[Dict]:
    """Пример списка транзакций для топ-5."""
    return [
        {"Дата операции": "10.02.2024 12:10:15", "Номер карты": "*1111", "Статус": "OK", "Сумма операции": -500},
        {"Дата операции": "12.02.2024 08:45:50", "Номер карты": "*2222", "Статус": "OK", "Сумма операции": -1500},
        {"Дата операции": "08.02.2024 14:20:30", "Номер карты": "*3333", "Статус": "OK", "Сумма операции": -200},
        {
            "Дата операции": "15.02.2024 19:00:05",
            "Номер карты": "*4444",
            "Статус": "OK",
            "Сумма операции": 300,
        },  # Доход
        {"Дата операции": "11.02.2024 09:35:20", "Номер карты": "*5555", "Статус": "OK", "Сумма операции": -100},
        {"Дата операции": "09.02.2024 07:25:10", "Номер карты": "*6666", "Статус": "OK", "Сумма операции": -400},
        {"Дата операции": "07.02.2024 22:15:40", "Номер карты": "*7777", "Статус": "OK", "Сумма операции": -50},
        {"Дата операции": "13.02.2024 17:50:00", "Номер карты": "*8888", "Статус": "OK", "Сумма операции": -900},
        {"Дата операции": "14.02.2024 11:55:25", "Номер карты": "*9999", "Статус": "OK", "Сумма операции": -1200},
    ]
