from os import getenv
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env")


class Config:
    BASE_DIR = BASE_DIR
    ENV = getenv("FLASK_ENV", "development")
    DEBUG = getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY = getenv("SECRET_KEY", "kjfssuer89fdskkbzvckaie*&q!@2ljbdsvk")
    LOG_DIR = BASE_DIR / "log"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {"development": DevelopmentConfig, "production": ProductionConfig}
