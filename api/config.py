from os import makedirs

import logging
from logging.handlers import RotatingFileHandler


formatter = logging.Formatter(
    "%(asctime)s\t[%(levelname)s]\t- %(module)s:(%(lineno)s) | %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger('FVM')
logger.setLevel(logging.INFO)

# Logger to Terminal
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

makedirs('log', exist_ok=True)
file_handler = RotatingFileHandler('log/api.log', maxBytes=10240)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)