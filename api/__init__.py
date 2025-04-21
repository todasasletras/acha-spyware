from .config import logger

from flask import Flask

from api.views import android_routes
from api.views.views import bp as views_bp
from api.controllers.mvt_controller import android_bp
from api.controllers.config_controller import config_bp


logger.debug("Função para definição do Flask.")


def create_app():
    app = Flask(__name__, static_folder="../frontend/static", static_url_path="/static")

    logger.debug("Registrando controladores de rotas")
    app.register_blueprint(android_routes.bp)
    # API
    app.register_blueprint(android_bp)
    app.register_blueprint(config_bp)
    # Frontend
    app.register_blueprint(views_bp)

    return app
