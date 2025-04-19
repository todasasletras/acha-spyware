from flask import Blueprint, render_template

from api import logger

bp = Blueprint("views", __name__, template_folder="../../frontend")


@bp.route("/")
def index():
    logger.debug("Carrega a pagina inicial")
    return render_template("index.html")


@bp.route("/info")
def info():
    logger.debug("Carrega a página de Informações")
    return render_template("info.html")


@bp.route("/report")
def report():
    logger.debug("Carregando a página do relatório")
    return render_template("report.html")
