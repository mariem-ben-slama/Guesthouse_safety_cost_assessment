from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Run the application
    # Debug mode is enabled by default for development
    # In production, you should set FLASK_DEBUG=False
    app.run(
        host='0.0.0.0',  # Makes the server accessible from outside
        port=5000,
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
    )