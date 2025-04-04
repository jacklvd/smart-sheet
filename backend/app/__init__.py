import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_relative_config=True)

    # Set up configuration
    from app.config import config_by_name

    config_obj = config_by_name.get(
        config_name or os.environ.get("FLASK_ENV", "development")
    )
    app.config.from_object(config_obj)

    # Set up logging
    # setup_logging(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Configure CORS properly
    # Allow requests from your frontend origin with credentials
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:3000",  # Add your production frontend URL
                ],
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )

    # Create instance directory if it doesn't exist
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        app.logger.warning(f"Error creating instance directory at {app.instance_path}")

    # Register blueprints
    from routes.routes import api_bp

    # NOTE: If your frontend calls /api/summarize, keep this prefix
    # If your frontend calls /summarize directly, remove the prefix
    app.register_blueprint(api_bp, url_prefix="/api")

    # register_error_handlers(app)

    app.logger.info(
        f"Application initialized with {config_name or os.environ.get('FLASK_ENV', 'development')} configuration"
    )
    app.logger.info(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.logger.info(
        f"Data cleanup interval: {app.config['DATA_CLEANUP_INTERVAL']} seconds"
    )
    app.logger.info(f"Data TTL: {app.config['DATA_TTL']}")

    return app
