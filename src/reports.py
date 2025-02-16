import json
import os
from datetime import datetime
from functools import wraps

from src.logger_config import add_logger

# Настройка логирования
logger = add_logger("reports.log", "reports")


def save_to_file(filename: str = None):
    """Декоратор, сохраняющий результат выполнения функции в JSON файл.
    Если имя файла не передано, используется имя по умолчанию."""

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)

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
                    json.dump(result, file, indent=4, ensure_ascii=False)
            except (OSError, json.JSONDecodeError) as e:
                logger.error(f"Ошибка при сохранении отчета в {report_file}: {e}")

            return result

        return wrapper

    return decorator
