import os
from typing import Dict, Union
from flask import Blueprint, jsonify, request
from app.controllers.mvt_controller import MVTController
from app.models.device import Device

bp = Blueprint('android_routes', __name__)
"""
Blueprint for Android-related routes.

This module defines endpoints to interact with the MVTController class,
allowing users to check devices connected via ADB and analyze APK files.
"""

@bp.route('/check-adb', methods=['POST'])
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
        Specify a path to the folder where JSON results will be stored (default: '/mnt/c/output').
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
    
    data = extract_request_data()
    if data['type'] == 'unsupported':
        return jsonify({'success': False, 'error': 'Unsupported content type'}), 200
    
    payload = data['data']
    serial = payload.get('serial', None)
    iocs_files = payload.get('iocs_files', None)
    output_folder = payload.get('output_folder', '/mnt/c/output')
    fast = payload.get('fast', False)
    list_modules = payload.get('list_modules', False)
    module = payload.get('module', None)
    non_interactive = payload.get('non_interactive', False)
    backup_password = payload.get('backup_password', None)
    verbose = payload.get('verbose', False)

    result = MVTController.check_adb(
        serial=serial,
        iocs_files=iocs_files,
        output_folder=output_folder,
        fast=fast,
        list_modules=list_modules,
        module=module,
        non_interactive=non_interactive,
        backup_password=backup_password,
        verbose=verbose
    )

    return jsonify(result), 200

@bp.route('/check-androidqf', methods=['POST'])
def check_androidqf():
    """
    Endpoint to analyze AndroidQF data for indicators of compromise (IOCs).

    Expects a JSON payload with the following parameters:
    
    Parameters
    ----------
    androidqf_path : str
        The path to the AndroidQF data to be analyzed (required).
    output_dir : str, optional
        Directory for saving the output (default: '/mnt/c/output').
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
    data = extract_request_data()
    if data['type'] == 'unsupported':
        return jsonify({'success': False, 'error': 'Unsupported content type'}), 200
    
    payload = data['data']
    if not payload.get('androidqf_path'):
        return jsonify({'success': False, 'error': 'Missing required parameter: androidqf_path'}), 200
    
    androidqf_path = payload.get('androidqf_path')
    output_dir = payload.get('output_dir', '/mnt/c/output')
    iocs_files = payload.get('iocs_files', [])
    list_modules = payload.get('list_modules', False)
    module = payload.get('module')
    hashes = payload.get('hashes', False)
    non_interactive = payload.get('non_interactive', False)
    backup_password = payload.get('backup_password')
    verbose = payload.get('verbose', False)

    result = MVTController.check_androidqf(
        androidqf_path=androidqf_path,
        iocs_files=iocs_files,
        output_folder=output_dir,
        list_modules=list_modules,
        module=module,
        hashes=hashes,
        non_interactive=non_interactive,
        backup_password=backup_password,
        verbose=verbose
    )
    
    return jsonify(result), 200

@bp.route('/check-backup', methods=['POST'])
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
    data = extract_request_data()
    if data['type'] == 'unsupported':
        return jsonify({'success': False, 'error': 'Unsupported content type'}), 200
    
    payload = data['data']
    if not payload.get('backup_path'):
        return jsonify({'success': False, 'error': 'Missing required parameter: backup_path'}), 200
    
    backup_path = payload.get('backup_path')
    iocs_files = payload.get('iocs_files')
    output_folder = payload.get('output_folder')
    list_modules =  payload.get('list_modules', False)
    non_interactive = payload.get('non_interactive', False)
    backup_password = payload.get('backup_password')
    verbose =  payload.get('verbose', False)

    result = MVTController.check_backup(
            backup_path=backup_path,
            iocs_files=iocs_files,
            output_folder=output_folder,
            list_modules=list_modules,
            non_interactive=non_interactive,
            backup_password=backup_password,
            verbose=verbose
        )

    return jsonify(result), 200

@bp.route('/check-bugreport', methods=['POST'])
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
    'output_folder': str, opotional Directory for saving the output (default is '/mnt/c/output').
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
    data = extract_request_data()
    if data['type'] == 'unsupported':
        return jsonify({'success': False, 'error': 'Unsupported content type'}), 200
    
    payload = data['data']
    if not payload.get('bugreport_path'):
        return jsonify({'success': False, 'error': 'Missing required parameter: bugreport_path'}), 200
    
    bugreport_path = payload.get('bugreport_path')
    iocs_files = payload.get('iocs_files')
    output_folder = payload.get('output_folder', '/mnt/c/output')
    list_modules = payload.get('list_modules', False)
    module = payload.get('module')
    verbose = payload.get('verbose', False)

    result = MVTController.check_bugreport(
        bugreport_path=bugreport_path,
        iocs_files=iocs_files,
        output_folder=output_folder,
        list_modules=list_modules,
        module=module,
        verbose=verbose
    )

    return jsonify(result)

@bp.route('/check-apk', methods=['POST'])
def check_apk():
    """
    Endpoint to analyze an APK file.

    Expects a JSON payload with:
    - 'file_path': Path to the APK file to be analyzed (required).
    - 'output_dir': Directory for saving the output (optional, defaults to '/mnt/c/output').

    Returns
    -------
    Response
        JSON object containing:
        - 'success' (bool): Indicates if the operation was successful.
        - 'stdout' (str, optional): Standard output if the operation succeeds.
        - 'stderr' (str, optional): Standard error if the operation fails.
    """
    data = request.json
    file_path = data.get('file_path')
    if not file_path:
        return jsonify({'success': False, 'error': 'Missing required parameter: file_path'}), 400

    output_dir = data.get('output_dir', '/mnt/c/output')
    result = MVTController.check_apk(file_path, output_dir)
    return jsonify(result)

@bp.route('/check-iocs', methods=['POST'])
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
    data = extract_request_data()
    if data['type'] == 'unsupported':
        return jsonify({'success':False, 'error': 'Unsupported content type'}), 200
    
    payload = data['data']
    if not payload.get('folder'):
        return jsonify({'success': False, 'error': 'Missing required parameter: folder.'}), 200
    
    folder = payload.get('folder')
    iocs_files = payload.get('iocs_files')
    list_modules = payload.get('list_modules', False)
    module = payload.get('module')

    result = MVTController.check_iocs(
            folder=folder,
            iocs_files=iocs_files,
            list_modules=list_modules,
            module=module
    )

    return jsonify(result), 200

@bp.route('/download-iocs', methods=['POST '])
def download_iocs():
    """
    Endpoit to download indicators of compromise (IOCs).

    Returns
    -------
    Response
        JSON object containing:
        - `success` (bool): Indicates if the operation was successful.
        - 'stdout' (str, optional): Standard output if the operation succeeds.
        - 'stderr' (str, optional): Standard error if the operation fails.
    """
    result = MVTController.download_iocs()
    return jsonify(result)

@bp.route('/download-apks', methods=['POST'])
def download_apks():
    """
    Endpoit to download indicators of compromise (IOCs).

    Parameters
    ----------
    - 'serial' (str, optional): Serial number of the device for downloading APKs.
    - 'all_apks' (bool, optional): Flag to download all APKs from the device (default is False).
    - 'virustotal (bool, optional): Flag to analyze APKs using VirusTotal (defalt is False).
    - 'output_folder' (str, optional): Directory for saving the downloaded APKs (defaults is '/mnt/c/output').
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
    data = extract_request_data()
    if data['type'] == 'unsupported':
        return jsonify({'success': False, 'error': 'Unsupported content type'}), 200
    
    payload = data['data']

    virustotal = payload.get('virustotal', False)
    if virustotal:
        var_env = 'MVT_VT_API_KEY'
        if var_env not in os.environ:
            return jsonify({'success': False, 'error': f'Missing environment variable: {var_env}'}), 200
    
    serial = payload.get('serial')
    all_apks = payload.get('all_apks', False)
    output_folder = payload.get('output_folder', '/mnt/c/output')
    from_file = payload.get('from_file')
    verbose = payload.get('verbose', False)

    result = MVTController.download_apks(
            serial=serial,
            all_apks=all_apks,
            virustotal=virustotal,
            output_folder=output_folder,
            from_file=from_file,
            verbose=verbose
        )
    
    return jsonify(result), 200

@bp.route('/devices', methods=['GET'])
def list_devices():
    """Endpoint to list connected devices.

    Retrieves a list of devices currently connected via ADB, using the Device model.

    Returns
    -------
    Response
        JSON array of device objects, where each object contains device details.
    
    """
    devices = Device.list_connected_devices()
    return jsonify([device.to_dict() for device in devices])

def extract_request_data()->Dict[str, Union[str, Dict[str, str]]]:
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
    if request.content_type is None:
        return {'type': 'unsupported', 'data': {'error': 'Unsupported Content Type None.'}}
    elif request.form:
        return {'type': 'form', 'data': request.form.to_dict() or {}}
    elif request.is_json:
        return{'type': 'json', 'data': request.json or {}}
    else:
        return {'type': 'unsupported', 'data': {'error': 'Unsupported Content Type'}}
    