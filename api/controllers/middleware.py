from flask import jsonify, request


def enforce_json_api(app):
    @app.before_request
    def check_json_for_api():
        if request.path.startswith("/api"):
            if not request.is_json:
                return jsonify(
                    {
                        "success": False,
                        "error": "Content-Type não aceito! Por favor utilize o 'Content-Type: application/json'",
                    }
                ), 200

    @app.after_request
    def set_json_content_type(response):
        if request.path.startswith("/api"):
            response.headers["Content-Type"] = "application/json"
        return response
