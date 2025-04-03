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
    setup_logging(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Create instance directory if it doesn't exist
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        app.logger.warning(f"Error creating instance directory at {app.instance_path}")

    from routes.routes import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    register_error_handlers(app)

    app.logger.info(
        f"Application initialized with {config_name or os.environ.get('FLASK_ENV', 'development')} configuration"
    )
    app.logger.info(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.logger.info(
        f"Data cleanup interval: {app.config['DATA_CLEANUP_INTERVAL']} seconds"
    )
    app.logger.info(f"Data TTL: {app.config['DATA_TTL']}")

    return app


def setup_logging(app):
    """Set up application logging"""
    if not app.debug and not app.testing:
        # Ensure log directory exists
        logs_dir = os.path.join(app.instance_path, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        # Set up file handler
        log_file = os.path.join(logs_dir, "app.log")
        file_handler = RotatingFileHandler(
            log_file, maxBytes=1024 * 1024 * 10, backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        file_handler.setLevel(logging.INFO)

        # Add handlers to app
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

        # Log startup
        app.logger.info("Application startup")


def register_error_handlers(app):
    """Register error handlers for the app"""

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"Not Found: {error}")
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Server Error: {error}")
        return {"error": "Server error, please try again later"}, 500
