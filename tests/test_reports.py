import json
import logging
from unittest.mock import patch

import pandas as pd

from src.reports import save_to_file, spending_by_category


def test_save_to_file_success(tmp_path) -> None:
    """Проверяет, создаётся ли JSON-файл и корректно ли записываются данные"""
    test_data_list = [{"Категория": "Продукты", "Сумма": 1000}]
    test_file_list = tmp_path / "test_report.json"

    @save_to_file(str(test_file_list))
    def mock_func():
        return test_data_list

    mock_func()
    assert test_file_list.exists()

    with open(test_file_list, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
        assert saved_data == test_data_list

    test_dataframe = pd.DataFrame({"Категория": ["Продукты"], "Сумма": [1000]})
    test_file_df = tmp_path / "test_report_df.json"

    @save_to_file(str(test_file_df))
    def mock_func_df():
        return test_dataframe

    mock_func_df()
    assert test_file_df.exists()

    with open(test_file_df, "r", encoding="utf-8") as f:
        saved_data_df = json.load(f)
        assert saved_data_df == [{"Категория": "Продукты", "Сумма": 1000}]


def test_save_to_file_error(caplog) -> None:
    """Проверяет, логируется ли ошибка при проблемах с записью JSON"""
    with patch("builtins.open", side_effect=OSError("Ошибка доступа")):

        @save_to_file("invalid_path.json")
        def mock_function():
            return {"key": "value"}

        with caplog.at_level(logging.ERROR):
            mock_function()

    assert any("Ошибка при сохранении отчета" in message for message in caplog.messages)


def test_spending_by_category_success(sample_transactions_df) -> None:
    """Проверяет, корректно ли фильтруются транзакции по категории и дате"""
    filtered_df = spending_by_category(sample_transactions_df, "Переводы", "2021-12-16")

    assert filtered_df == [
        {"Дата операции": "2021-12-15 10:30:00", "Категория": "Переводы", "Сумма": 5000},
        {"Дата операции": "2021-12-05 18:45:00", "Категория": "Переводы", "Сумма": 2000},
    ]


def test_spending_by_category_invalid(sample_transactions_df, caplog) -> None:
    """Проверяет, что при отсутствии данных в категории возвращается пустой DataFrame"""
    with caplog.at_level(logging.WARNING):
        filtered_df = spending_by_category(sample_transactions_df, "Развлечения", "2021-12-16")

    assert len(filtered_df) == 0
    assert any("Нет данных по категории 'Развлечения'" in message for message in caplog.messages)
