from flask import Flask, jsonify, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from app.config import Config
from app.models import db
import os

def create_app(config_class=Config):
    """
    Application factory function.
    This creates and configures the Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Ensure the instance folder exists (where the database will be stored)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Initialize extensions
    db.init_app(app)  # Database
    JWTManager(app)   # JWT authentication
    CORS(app)         # Allow cross-origin requests (useful for testing)
    
    # Create a route to serve the swagger.yml file
    @app.route('/swagger.yml')
    def swagger_spec():
        swagger_path = os.path.join(app.root_path, '..', 'static')
        return send_from_directory(swagger_path, 'swagger.yml')
    
    # Configure Swagger UI for API documentation
    SWAGGER_URL = '/api/docs'
    API_URL = '/swagger.yml'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Guesthouse Safety API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Register blueprints (routes)
    from app.auth import auth_bp
    from app.guesthouses import guesthouses_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(guesthouses_bp)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Welcome to Guesthouse Safety API',
            'version': app.config['API_VERSION'],
            'endpoints': {
                'documentation': '/api/docs',
                'authentication': '/api/auth',
                'guesthouses': '/api/guesthouses'
            }
        })
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app