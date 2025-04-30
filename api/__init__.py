from flask import Flask

from core.logger import setup_logger
from api.controllers.middleware import enforce_json_api
from api.views import android_routes
from api.views.views import bp as views_bp
from api.controllers import api_bp

logger = setup_logger()

logger.debug("Função para definição do Flask.")


def create_app():
    app = Flask(__name__, static_folder="../frontend/static", static_url_path="/static")

    logger.debug("Registrando controladores de rotas")
    app.register_blueprint(android_routes.bp)  # remover esse registro futuramente
    # API
    app.register_blueprint(api_bp)
    # Frontend
    app.register_blueprint(views_bp)

    enforce_json_api(app)

    return app
