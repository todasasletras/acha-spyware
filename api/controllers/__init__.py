from flask import Blueprint, jsonify

from api.exceptions.base import APIException
from core.logger import setup_logger

# Importa e registra os módulos
from .mvt_controller import android_bp
from .config_controller import config_bp

logger = setup_logger(__name__)
# Blueprint raiz da API
api_bp = Blueprint("api", __name__, url_prefix="/api")


api_bp.register_blueprint(android_bp)
api_bp.register_blueprint(config_bp)


@api_bp.errorhandler(APIException)
def handler_api_exception(error):
    logger.error(error.to_log())
    return jsonify(error.to_dict()), 200
