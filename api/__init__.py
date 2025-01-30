from flask import Flask
from api.views import android_routes

def create_app():
    app = Flask(__name__)

    app.register_blueprint(android_routes.bp)

    return app
