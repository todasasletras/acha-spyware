from flask import Blueprint, jsonify, request

from api.exceptions.config import ConfigException, MissingAPIKeyException
from api.models.types.schemas import APIResponse
from api.services.config_service import ConfigService

MVT_VT_API_KEY = "MVT_VT_API_KEY"

config_bp = Blueprint("config", __name__, url_prefix="/config")

config = ConfigService()


@config_bp.route("/set-vt-key", methods=["POST"])
def set_vt_key():
    try:
        data = request.json
        key = data.get("api_key", {})
        if not key:
            raise MissingAPIKeyException()
        print(key)
        result = config.set_env_variable(MVT_VT_API_KEY, key)
        print(result)
        response = APIResponse(success=True, messages=result["message"])
        return jsonify(response), 200
    except ConfigException as ce:
        return jsonify({"success": False, "error": ce.message}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 200
