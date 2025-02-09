import logging

from dateutil import parser

# Настройка логирования
logger = logging.getLogger("views")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("logs/views.log", mode="w", encoding="UTF-8")
file_formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(levelname)s: %(message)s", datefmt="%d-%m-%Y %H:%M:%S"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_greeting(current_time: str) -> str:
    """
    Функция подбирает необходимое приветствие в соответствии с текущим временем суток.
    :param current_time: Строка с текущим временем в формате ISO-8601.
    :return: Строка с приветствием.
    """
    try:
        logger.info(f"Вызов функции 'get_greeting' с параметром '{current_time}'.")
        hour = parser.isoparse(current_time).hour
        if 12 > hour >= 6:
            logger.info("Определено приветствие: 'Доброе утро'.")
            return "Доброе утро"
        elif 18 > hour >= 12:
            logger.info("Определено приветствие: 'Добрый день'.")
            return "Добрый день"
        elif 6 > hour >= 0:
            logger.info("Определено приветствие: 'Доброй ночи'.")
            return "Доброй ночи"
        else:
            logger.info("Определено приветствие: 'Добрый вечер'.")
            return "Добрый вечер"

    except (TypeError, ValueError) as e:
        logger.error(f"Ошибка обработки даты: {e}", exc_info=True)
        return "Ошибка: некорректная дата"
