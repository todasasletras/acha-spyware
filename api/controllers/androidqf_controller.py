from typing import List, Dict, Union

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

from core.logger import setup_logger
from api.models.types.schemas import APIResponse, LogMessageEntry
from api.services.command_executor import CommandExecutor
from api.services.mvt_service import MVTAndroid

logger = setup_logger(__name__)
ENV_FILE = ".env"
logger.debug("Carregar variáveis de ambiente")
load_dotenv()

android_bp = Blueprint("android", __name__, url_prefix="/android")


@android_bp.route("/check-adb", methods=["POST"])
def check_adb():
    data = request.json
    mvt_android = MVTAndroid(CommandExecutor())
    result: LogMessageEntry = mvt_android.check_adb(**data)
    response: APIResponse = {
        "success": True,
        "logs": result["logs"],
        "messages": result["messages"],
    }
    return jsonify(response), 200


def runAndroidqf(globalFolder):
    """
    - Executes androidqf binary with output path.
    - Generates a unique subfolder inside the specified output folder.
    """

    config = utils.readConfig()

    if not os.path.isabs(globalFolder):
        globalFolder = config.baseOutput + globalFolder
    fullOutPath = globalFolder + "/" + str(uuid.uuid4())  # ejecición del binario
    if acquisition.createFolder(fullOutPath):
        if not acquisition.runMyProcess(
            [config.androidqfPath + config.androidqfBinary, "-o", fullOutPath],
            config.androidqfPath,
        ):
            print("Couldn't get androidqf acquisition")
            return False

        print("androidqf acquisition completed")
        return True
    else:
        print("Couldn't create folder for androidqf acquisition")
        return False
