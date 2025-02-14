from flask import Flask, jsonify
from api.views import android_routes
from api.views.views import bp as views_bp


def create_app():
    app = Flask(__name__, static_folder='../frontend/static', static_url_path='/static')

    # Registrando controladores de rotas
    app.register_blueprint(android_routes.bp)

    app.register_blueprint(views_bp)

    return app
