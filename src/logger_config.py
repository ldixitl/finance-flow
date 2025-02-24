import logging
import os


def add_logger(log_filename: str, logger_name: str) -> logging.Logger:
    """
    Создаёт и настраивает логгер с записью в папке 'logs' в корне проекта.
    :param log_filename: Имя файла логов.
    :param logger_name: Название логгера.
    :return: Настроенный объект логгера.
    """
    path_module = os.path.abspath(os.path.dirname(__file__))
    path_project = os.path.dirname(path_module)

    logs_dir = os.path.join(path_project, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    log_file_path = os.path.join(logs_dir, log_filename)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file_path, mode="w", encoding="UTF-8")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(filename)s - %(levelname)s: %(message)s", datefmt="%d-%m-%Y %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    if not logger.hasHandlers():
        logger.addHandler(file_handler)

    return logger
