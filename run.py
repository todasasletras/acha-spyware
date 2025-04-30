from core.logger import setup_logger
from api import create_app

logger = setup_logger()
logger.info("Inicio do FVM!")

logger.debug("Criar uma instancia de aplicação Flask.")
app = create_app()

if __name__ == "__main__":
    """
    Run the Flask application in debug mode.

    This block checks if the script is being executed directly, and if so, 
    it starts the Flask development server with debug mode enabled.
    """
    logger.debug("Inicio do servidor Flask.")
    app.run(debug=True)
