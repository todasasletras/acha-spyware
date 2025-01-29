from flask import Flask
from app.views import android_routes

def create_app():
    app = Flask(__name__)

    app.register_blueprint(android_routes.bp)

    return app
