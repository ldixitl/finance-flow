import json
from unittest.mock import patch

import pandas as pd

from src.views import main_view


@patch("src.views.transaction_parser")
@patch("src.views.filter_transactions_by_month")
@patch("src.views.cost_analysis")
@patch("src.views.get_top_transactions")
@patch("src.views.currency_exchanger")
@patch("src.views.stock_exchanger")
def test_main_view_success(
    mock_stock_exchanger,
    mock_currency_exchanger,
    mock_get_top_transactions,
    mock_cost_analysis,
    mock_filter_transactions_by_month,
    mock_transaction_parser,
    mock_transactions_df,
):
    """Тест успешной работы main_view."""

    # Настройка моков
    mock_transaction_parser.return_value = mock_transactions_df
    mock_filter_transactions_by_month.return_value = mock_transactions_df
    mock_cost_analysis.return_value = pd.DataFrame({"last_digits": ["1234"], "total_spent": [500], "cashback": [5]})
    mock_get_top_transactions.return_value = pd.DataFrame(
        {"date": ["2024-02-10"], "amount": [-500], "category": ["Еда"], "description": ["Кафе"]}
    )
    mock_currency_exchanger.return_value = [{"currency": "USD", "rate": 88.64}]
    mock_stock_exchanger.return_value = [{"stock": "AAPL", "price": 145.32}]

    # Вызов тестируемой функции
    response_json = main_view("2024-02-11 12:00:00", "data/operations.xlsx")

    # Проверяем, что JSON-ответ корректный
    response = json.loads(response_json)
    assert "greeting" in response
    assert "cards" in response
    assert "top_transactions" in response
    assert "currency_rates" in response
    assert "stock_rates" in response
    assert len(response["cards"]) == 1
    assert len(response["top_transactions"]) == 1
    assert len(response["currency_rates"]) == 1
    assert len(response["stock_rates"]) == 1


@patch("src.views.transaction_parser", side_effect=Exception("Ошибка загрузки транзакций"))
def test_main_view_error(mock_transaction_parser):
    """Тест обработки ошибок в main_view."""
    response_json = main_view("2024-02-11 12:00:00", "data/operations.xlsx")
    response = json.loads(response_json)
    assert "error" in response
    assert response["error"] == "Произошла ошибка при обработке запроса."
