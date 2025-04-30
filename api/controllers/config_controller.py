from flask import Blueprint, jsonify, request

from api.exceptions.config_except import MissingParameterException, ParamenterInvalid
from api.models.types.schemas import APIResponse
from api.services.config_service import ConfigService
from core.logger import setup_logger

logger = setup_logger(__name__)

MVT_VT_API_KEY = "MVT_VT_API_KEY"

config_bp = Blueprint("config", __name__, url_prefix="/config")

config = ConfigService()


@config_bp.route("/set-vt-key", methods=["POST"])
def set_vt_key():
    data = request.json
    key = data.get("api_key", {})

    if not data:
        miss_param_error = MissingParameterException(
            {"error": "Não possui parâmetros.", "parameter": data}
        )
        logger.warning(miss_param_error.to_log())
        raise miss_param_error

    if not key:
        param_inv_error = ParamenterInvalid(
            {"error": "O parâmetro 'api_key' não está presente.", "parameter": data}
        )
        logger.warning(param_inv_error.to_log())
        raise param_inv_error

    result = config.set_env_variable(MVT_VT_API_KEY, key)
    response = APIResponse(success=True, messages=result["message"])

    return jsonify(response), 200
