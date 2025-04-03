import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""

    # Basic Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard-to-guess-string"
    DEBUG = False
    TESTING = False

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "../instance/app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload

    # Summary settings
    MAX_SUMMARY_LENGTH = 2000  # Maximum number of words for a summary
    DEFAULT_SUMMARY_LENGTH = 200  # Default summary length

    # Data cleanup settings
    DATA_CLEANUP_INTERVAL = int(
        os.environ.get("DATA_CLEANUP_INTERVAL", 3600)
    )  # Default 1 hour
    MAX_RECORDS_PER_TABLE = int(
        os.environ.get("MAX_RECORDS_PER_TABLE", 1000)
    )  # Default 1000 records
    DATA_TTL = timedelta(hours=1)  # Time-to-live for database records


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Faster cleanup for testing
    DATA_CLEANUP_INTERVAL = 60  # 1 minute
    DATA_TTL = timedelta(minutes=5)


class ProductionConfig(Config):
    """Production configuration"""

    # Production-specific settings
    DEBUG = False

    # Use stronger secret key in production
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # More conservative data retention in production
    DATA_TTL = timedelta(hours=24)  # Keep data for 24 hours in production


# Select configuration based on environment
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

# Default to development config
Config = config_by_name[os.environ.get("FLASK_ENV", "development")]
