from flask import Blueprint, render_template

from api import logger

bp = Blueprint('views', __name__, template_folder='../../frontend')

@bp.route('/')
def index():
    logger.debug("Carrega a pagina inicial")
    return render_template('index.html')
