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

    Expects a JSON payload with an optional 'output_dir' key to specify the 
    directory for saving the output. Defaults to '/mnt/c/output'.

    Returns
    -------
    Response
        JSON object containing:
        - 'success' (bool): Indicates if the operation was successful.
        - 'stdout' (str, optional): Standard output if the operation succeeds.
        - 'stderr' (str, optional): Standard error if the operation fails.
    """
    data = request.json
    output_dir = data.get('output_dir', '/mnt/c/output')
    result = MVTController.check_adb(output_dir)
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

    Expects a JSON payload with:
    - 'output_dir': Directory for saving the downloaded APKs (optional, defaults to '/mnt/c/output').
    - 'analyze': Boolean flag to determine if the APKs should be analyzed (optional, defaults to False).

    Returns
    -------
    Response
        JSON object containing:
        - `success` (bool): Indicates if the operation was successful.
        - 'stdout' (str, optional): Standard output if the operation succeeds.
        - 'stderr' (str, optional): Standard error if the operation fails.
    """
    data = request.json
    output_dir = data.get('output_dir', '/mnt/c/output')
    analyze = data.get('analyze', False)
    result = MVTController.download_apks(output_dir, analyze)
    return jsonify(result)

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