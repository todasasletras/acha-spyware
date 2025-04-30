import os
from dotenv import load_dotenv
from typing import Dict, Union
from flask import Blueprint, jsonify, request
from core.logger import setup_logger
from api.controllers.mvt_controller import MVTController
from api.models.device import Device

logger = setup_logger()
ENV_FILE = ".env"
logger.debug("Carregar variaveis de ambiente")
load_dotenv()

bp = Blueprint("android_routes", __name__)
"""
Blueprint for Android-related routes.

This module defines endpoints to interact with the MVTController class,
allowing users to check devices connected via ADB and analyze APK files.
"""


@bp.route("/check-adb", methods=["POST"])
def check_adb():
    """
    Endpoint to check devices connected via ADB.

    Expects a payload that can be in JSON or form-data format. The payload may include:

    Parameters
    ----------
    serial : str, optional
        Specify a device serial number or HOST:PORT connection string.
    iocs_files : list, optional
        A list of paths to indicators files. Can include multiple files.
    output_folder : str, optional
        Specify a path to the folder where JSON results will be stored (default: '/tmp/fvm').
    fast : bool, optional
        Skip time/resource-consuming features (default: False).
    list_modules : bool, optional
        If True, lists available modules and exits (default: False).
    module : str, optional
        Name of a single module to run instead of all.
    non_interactive : bool, optional
        Avoid interactive questions during processing (default: False).
    backup_password : str, optional
        Backup password to use for an Android backup.
    verbose : bool, optional
        If True, enables verbose mode (default: False).

    Returns
    -------
    Response
        JSON object containing:
        - 'success' (bool): Indicates if the operation was successful.
        - 'stdout' (str, optional): Standard output if the operation succeeds.
        - 'stderr' (str, optional): Standard error if the operation fails.
    """
    logger.debug("Inicio do check-adb")
    data = extract_request_data()
    if data["type"] == "unsupported":
        logger.warning("Tipo de content type nao suportado.")
        return jsonify({"success": False, "error": "Unsupported content type"}), 200

    payload = data["data"]
    serial = payload.get("serial", None)
    iocs_files = payload.get("iocs_files", None)
    output_folder = payload.get("output_folder", "/tmp/fvm")
    fast = payload.get("fast", False)
    list_modules = payload.get("list_modules", False)
    module = payload.get("module", None)
    non_interactive = payload.get("non_interactive", False)
    backup_password = payload.get("backup_password", None)
    verbose = payload.get("verbose", False)

    logger.debug("Executar o comando check-adb.")
    result = MVTController.check_adb(
        serial=serial,
        iocs_files=iocs_files,
        output_folder=output_folder,
        fast=fast,
        list_modules=list_modules,
        module=module,
        non_interactive=non_interactive,
        backup_password=backup_password,
        verbose=verbose,
    )

    logger.debug("Retorna o resultado do comando")
    return jsonify(result), 200


@bp.route("/check-androidqf", methods=["POST"])
def check_androidqf():
    """
    Endpoint to analyze AndroidQF data for indicators of compromise (IOCs).

    Expects a JSON payload with the following parameters:

    Parameters
    ----------
    androidqf_path : str
        The path to the AndroidQF data to be analyzed (required).
    output_dir : str, optional
        Directory for saving the output (default: '/tmp/fvm').
    iocs_files : list, optional
        A list of paths to indicators of compromise (optional).
    list_modules : bool, optional
        Flag to list available modules (default: False).
    module : str, optional
        Name of a specific module to run.
    hashes : bool, optional
        Flag to generate hashes of analyzed files (default: False).
    non_interactive : bool, optional
        Avoid interactive questions during processing (default: False).
    backup_password : str, optional
        Password for an Android backup (default: None).
    verbose : bool, optional
        Enables verbose mode (default: False).

    Returns
    -------
    Response
        JSON object containing:
        - 'success' (bool): Indicates if the operation was successful.
        - 'stdout' (str, optional): Standard output if the operation succeeds.
        - 'stderr' (str, optional): Standard error if the operation fails.
    """
    logger.debug("Inicio do androidqf")
    data = extract_request_data()
    if data["type"] == "unsupported":
        logger.warning("Tipo de content type nao suportado.")
        return jsonify({"success": False, "error": "Unsupported content type"}), 200

    payload = data["data"]
    if not payload.get("androidqf_path"):
        logger.warning("Falto de parametro: androidqf_path .")
        return jsonify(
            {"success": False, "error": "Missing required parameter: androidqf_path"}
        ), 200

    androidqf_path = payload.get("androidqf_path")
    output_dir = payload.get("output_dir", "/tmp/fvm")
    iocs_files = payload.get("iocs_files", [])
    list_modules = payload.get("list_modules", False)
    module = payload.get("module")
    hashes = payload.get("hashes", False)
    non_interactive = payload.get("non_interactive", False)
    backup_password = payload.get("backup_password")
    verbose = payload.get("verbose", False)

    logger.debug("Executar o comando androidqf.")
    result = MVTController.check_androidqf(
        androidqf_path=androidqf_path,
        iocs_files=iocs_files,
        output_folder=output_dir,
        list_modules=list_modules,
        module=module,
        hashes=hashes,
        non_interactive=non_interactive,
        backup_password=backup_password,
        verbose=verbose,
    )

    logger.debug("Retorna o resultado do comando")
    return jsonify(result), 200


@bp.route("/check-backup", methods=["POST"])
def check_backup():
    """
    Endpoint to analyze Android backup data for indicators of compromise (IOCs).

    Parameters
    ----------
    'backup_path': str, required
        Path to the Android backup to be analyzed.
    'iocs_files': str, optional
        A list of paths to indicators of compromise.
    'output_folder': str, optional
        Directory for saving the output.
    'list_modules': bool, optional
        Boolean flag to list available modules (default is False).
    'non_interactive': bool, optional
        Boolean flag to avoid interactive questions (default is False).
    'backup_password': str, optional
        Password for decrypting the Android backup.
    'verbose': str, optional
        Boolean flag to enable verbose mode (default is False).

    Returns
    -------
    Response
        JSON object containing:
        - 'success' (bool): Indicates if the operation was successful.
        - 'stdout' (str, optional): Standard output if the operation succeeds.
        - 'stderr' (str, optional): Standard error if the operation fails.
    """
    logger.debug("Inicio do check-backup")
    data = extract_request_data()
    if data["type"] == "unsupported":
        logger.warning("Tipo de content type nao suportado.")
        return jsonify({"success": False, "error": "Unsupported content type"}), 200

    payload = data["data"]
    if not payload.get("backup_path"):
        logger.warning("Falto de parametro: backup_path.")
        return jsonify(
            {"success": False, "error": "Missing required parameter: backup_path"}
        ), 200

    backup_path = payload.get("backup_path")
    iocs_files = payload.get("iocs_files")
    output_folder = payload.get("output_folder")
    list_modules = payload.get("list_modules", False)
    non_interactive = payload.get("non_interactive", False)
    backup_password = payload.get("backup_password")
    verbose = payload.get("verbose", False)

    logger.debug("Executar o comando chek-backup.")
    result = MVTController.check_backup(
        backup_path=backup_path,
        iocs_files=iocs_files,
        output_folder=output_folder,
        list_modules=list_modules,
        non_interactive=non_interactive,
        backup_password=backup_password,
        verbose=verbose,
    )

    logger.debug("Retorna o resultado do comando")
    return jsonify(result), 200


@bp.route("/check-bugreport", methods=["POST"])
def check_bugreport():
    """
    Endpoint to analyze Android bugreport data for indicators of compromise (IOCs).

    Expects a JSON payload with the following parameters:

    Parameters
    ----------
    'bugreport_path': str, required
        Path to the bugreport file to be analyzed.
    'iocs_files': list, optional
        A list of paths to indicators of compromise.
    'output_folder': str, opotional Directory for saving the output (default is '/tmp/fvm').
    'list_modules': bool, option
        Boolean flag to list available modules (default is False).
    'module': str, optional
        Name of a specific module to run.
    'verbose': bool, optional
        Boolean flag to enable verbose mode (default is False).

    Returns
    -------
    Response
        JSON object containing:
        - 'success' (bool): Indicates if the operation was successful.
        - 'stdout' (str, optional): Standard output if the operation succeeds.
        - 'stderr' (str, optional): Standard error if the operation fails.
    """
    logger.debug("Inicio do check-bugreport")
    data = extract_request_data()
    if data["type"] == "unsupported":
        logger.warning("Tipo de content type nao suportado.")
        return jsonify({"success": False, "error": "Unsupported content type"}), 200

    payload = data["data"]
    if not payload.get("bugreport_path"):
        logger.warning("Falto de parametro: bugreport_path.")
        return jsonify(
            {"success": False, "error": "Missing required parameter: bugreport_path"}
        ), 200

    bugreport_path = payload.get("bugreport_path")
    iocs_files = payload.get("iocs_files")
    output_folder = payload.get("output_folder", "/tmp/fvm")
    list_modules = payload.get("list_modules", False)
    module = payload.get("module")
    verbose = payload.get("verbose", False)

    logger.debug("Executar o comando chek-backup.")
    result = MVTController.check_bugreport(
        bugreport_path=bugreport_path,
        iocs_files=iocs_files,
        output_folder=output_folder,
        list_modules=list_modules,
        module=module,
        verbose=verbose,
    )

    logger.debug("Retorna o resultado do comando")
    return jsonify(result), 200


@bp.route("/check-apk", methods=["POST"])
def check_apk():
    """
    Endpoint to analyze an APK file.

    Expects a JSON payload with:
    - 'file_path': Path to the APK file to be analyzed (required).
    - 'output_dir': Directory for saving the output (optional, defaults to '/tmp/fvm').

    Returns
    -------
    Response
        JSON object containing:
        - 'success' (bool): Indicates if the operation was successful.
        - 'stdout' (str, optional): Standard output if the operation succeeds.
        - 'stderr' (str, optional): Standard error if the operation fails.
    """
    data = request.json
    file_path = data.get("file_path")
    if not file_path:
        return jsonify(
            {"success": False, "error": "Missing required parameter: file_path"}
        ), 400

    output_dir = data.get("output_dir", "/tmp/fvm")
    result = MVTController.check_apk(file_path, output_dir)
    return jsonify(result)


@bp.route("/check-iocs", methods=["POST"])
def check_iocs():
    """
    Endpoit to analyze files in a folder against provided Indicators of Compromise (IOCs).

    Parameters
    ----------
    - 'folder' (str, required): Path to the folder containing files to analyze.
    - 'iocs_files' (List[str], optional): A list of IOC files to use for analysis.
    - 'list_modules' (bool, optional): Boolean flag to list avaliable modules (default is False).
    - 'module' (str, optional): Name of a specific module to run.

    Returns
    -------
    Response
        JSON object containing:
        - 'success (bool): Indicates if the operation was successful.
        - 'output' (str, optional): Standard output if the operation succeeds.
        - 'error' (str, optional): Standard error if the operation fails.
    """
    logger.debug("Inicio do check-iocs")
    data = extract_request_data()
    if data["type"] == "unsupported":
        logger.warning("Tipo de content type nao suportado.")
        return jsonify({"success": False, "error": "Unsupported content type"}), 200

    payload = data["data"]
    if not payload.get("folder"):
        logger.warning("Falto de parametro: folder.")
        return jsonify(
            {"success": False, "error": "Missing required parameter: folder."}
        ), 200

    folder = payload.get("folder")
    iocs_files = payload.get("iocs_files")
    list_modules = payload.get("list_modules", False)
    module = payload.get("module")

    logger.debug("Executar o comando chek-iocs.")
    result = MVTController.check_iocs(
        folder=folder, iocs_files=iocs_files, list_modules=list_modules, module=module
    )

    logger.debug("Retorna o resultado do comando")
    return jsonify(result), 200


@bp.route("/download-iocs", methods=["POST", "GET"])
def download_iocs():
    """
    Endpoit to download indicators of compromise (IOCs).

    Returns
    -------
    Response
        JSON object containing:
        - `success` (bool): Indicates if the operation was successful.
        - 'message' (str, optional): Standard output if the operation succeeds.
        - 'error' (str, optional): Standard error if the operation fails.
    """
    logger.debug("Inicio do download-iocs")
    logger.debug("Executar o comando download-iocs.")
    result = MVTController.download_iocs()

    logger.debug("Retorna o resultado do comando")
    return jsonify(result), 200


@bp.route("/download-apks", methods=["POST"])
def download_apks():
    """
    Endpoit to download indicators of compromise (IOCs).

    Parameters
    ----------
    - 'serial' (str, optional): Serial number of the device for downloading APKs.
    - 'all_apks' (bool, optional): Flag to download all APKs from the device (default is False).
    - 'virustotal (bool, optional): Flag to analyze APKs using VirusTotal (defalt is False).
    - 'output_folder' (str, optional): Directory for saving the downloaded APKs (defaults is '/tmp/fvm').
    - 'from_file' (str, optional): Path to a file containing a list of APKs to download.
    - 'verbose' (bool, optional): Flag to enable verbose output (default is False)

    Returns
    -------
    Response
        JSON object containing:
        - `success` (bool): Indicates if the operation was successful.
        - 'output' (str, optional): Standard output if the operation succeeds.
        - 'error' (str, optional): Standard error if the operation fails.
    """
    logger.debug("Inicio do download-apks")
    data = extract_request_data()
    if data["type"] == "unsupported":
        logger.warning("Tipo de content type nao suportado.")
        return jsonify({"success": False, "error": "Unsupported content type"}), 200

    payload = data["data"]

    virustotal = payload.get("virustotal", False)

    if virustotal:
        var_env = "MVT_VT_API_KEY"
        if var_env not in os.environ:
            logger.warning("Variável de ambiente MVT_VT_API_KEY não definida.")
            return jsonify(
                {"success": False, "error": f"Missing environment variable: {var_env}"}
            ), 200

    serial = payload.get("serial")
    all_apks = payload.get("all_apks", False)
    output_folder = payload.get("output_folder", "/tmp/fvm")
    from_file = payload.get("from_file")
    verbose = payload.get("verbose", False)

    logger.debug("Executar o comando download-apks.")
    result = MVTController.download_apks(
        serial=serial,
        all_apks=all_apks,
        virustotal=virustotal,
        output_folder=output_folder,
        from_file=from_file,
        verbose=verbose,
    )

    logger.debug("Retorna o resultado do comando")
    return jsonify(result), 200


@bp.route("/devices", methods=["GET"])
def list_devices():
    """Endpoint to list connected devices.

    Retrieves a list of devices currently connected via ADB, using the Device model.

    Returns
    -------
    Response
        JSON array of device objects, where each object contains device details.

    """
    logger.debug("Inicio do list-devices")
    logger.debug("Exdecutar a listagem de dispositivos.")
    devices = Device.list_connected_devices()

    logger.debug("Retorna o resultado do comando")
    return jsonify([device.to_dict() for device in devices])


@bp.route("/set-virustotal-api-key", methods=["POST"])
def set_virustotal_api_key():
    logger.debug("Início do set-virustotal-api-key")
    data = extract_request_data()
    if data["type"] == "unsupported":
        logger.warning("Tipo de content type não suportado.")
        return jsonify({"success": False, "error": data["data"]["error"]}), 200

    payload = data["data"]
    if not payload.get("api_key"):
        logger.warning("Falta do parâmetro: api_key.")
        return jsonify(
            {"success": False, "error": "Missing required parameter: api_key"}
        )

    var_env = "MVT_VT_API_KEY"
    api_key = payload["api_key"]
    new_env = f"{var_env}={api_key}\n"

    try:
        if not os.path.exists(ENV_FILE):
            with open(ENV_FILE, "w") as file:
                file.write(new_env)
        else:
            updated = False
            with open(ENV_FILE, "r") as file:
                lines = file.readlines()

            with open(ENV_FILE, "w") as file:
                for line in lines:
                    if line.startswith(var_env):
                        file.write(new_env)
                        updated = True
                    else:
                        file.write(line)
                if not updated:
                    file.write(new_env)

        # Recarrega o .env no ambiente
        load_dotenv(ENV_FILE)

        return jsonify(
            {"success": True, "message": "VirusTotal API Key set successfully"}
        ), 200

    except Exception as e:
        logger.error(f"Failed to set API Key: {e}")
        return jsonify({"success": False, "error": "Failed to set API Key."}), 200


def extract_request_data() -> Dict[str, Union[str, Dict[str, str]]]:
    """
    Extract data from the incoming request, identifying if it's a form or JSON payload.

    This function check the content type of the incoming request and parses it accordingly.
    If the content type is not supported, it returns an error message.

    Returns
    -------
    Dict[str, Union[str, Dict[str, str]]]
        A dictionary containig:
        - 'type' (str): Indicates the content type of the request ('form', 'json', 'unsupported')
        - 'data' (dict): The parsed form or json data (error message if unsupported).
    """
    logger.debug("Inicio do extract-request-data")
    if request.content_type is None:
        logger.debug(f"O Content type é {request.content_type}")
        return {
            "type": "unsupported",
            "data": {"error": "Unsupported Content Type None."},
        }
    elif request.form:
        logger.debug("Obtendo os parametros do form.")
        return {"type": "form", "data": request.form.to_dict() or {}}
    elif request.is_json:
        logger.debug("Obtendo os parametros do json.")
        return {"type": "json", "data": request.json or {}}
    else:
        logger.debug(f"O Content type não é suportado: {request.content_type}")
        return {"type": "unsupported", "data": {"error": "Unsupported Content Type"}}


# Erros de requisições
@bp.app_errorhandler(400)
def bad_request(error):
    return jsonify(
        {"success": False, "error": "Requisição inválida. Verifique os dados enviados."}
    ), 200


@bp.app_errorhandler(404)
def not_found(error):
    logger.error(f"Endpoint não encontrado: {error}")
    return jsonify({"success": False, "error": "Esta página não existe."}), 200


@bp.app_errorhandler(405)
def method_not_allowed(error):
    return jsonify(
        {
            "success": False,
            "error": "Método não permitido. Verifique a documentação da API.",
        }
    ), 200


@bp.app_errorhandler(500)
def internal_server_error(error):
    return jsonify(
        {
            "success": False,
            "error": "Erro interno do servidor. Tente novamente mais tarde",
        }
    ), 200
