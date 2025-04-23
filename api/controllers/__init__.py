from flask import Blueprint

# Importa e registra os módulos
from .mvt_controller import android_bp
from .config_controller import config_bp

# Blueprint raiz da API
api_bp = Blueprint("api", __name__, url_prefix="/api")


api_bp.register_blueprint(android_bp)
api_bp.register_blueprint(config_bp)
