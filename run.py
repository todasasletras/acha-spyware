from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    """
    Run the Flask application in debug mode.

    This block checks if the script is being executed directly, and if so, 
    it starts the Flask development server with debug mode enabled.
    """
    app.run(debug=True)
