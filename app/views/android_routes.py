from flask import Blueprint, jsonify, request
from app.controllers.mvt_controller import MVTController

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
