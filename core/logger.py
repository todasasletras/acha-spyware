import logging
from logging.handlers import RotatingFileHandler
from configuration.settings import Config


def setup_logger(name="FVM") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        if not Config.LOG_DIR.exists():
            Config.LOG_DIR.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter(
            "[%(asctime)s]\t[%(levelname)s]\t- "
            "[%(module)s:(%(lineno)s) | %(funcName)s]\t- "
            "%(message)s",
            datetime="%Y-%m-%d %H:%M:%S",
        )

        file_handler = RotatingFileHandler(
            Config.LOG_DIR / "fvm.log", maxBytes=2 * 1024 * 1024, backupCount=1
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
