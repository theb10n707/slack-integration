import os

from app.config import BaseConfig
from app.utils.utils import configure_logging, init_celery, make_celery
from dotenv import load_dotenv
from flask import Flask
from flask_mongoengine import MongoEngine

mongo_db = MongoEngine()
celery = make_celery()
# Load environment variables
load_dotenv()


def create_app() -> Flask:
    app = Flask(BaseConfig.APP_NAME)
    app.debug = BaseConfig.DEBUG
    app_settings = os.getenv("FLASK_CONFIG", BaseConfig)
    app.config.from_object(app_settings)
    # Register Mongo DB
    mongo_db.init_app(app)
    # Setup Celery
    init_celery(celery=celery, app=app)
    # Set Logging Level
    configure_logging(app=app)
    # Register API Routes
    from app.server import app_blueprints
    from app.commands import commands_blueprints
    app.register_blueprint(app_blueprints)
    app.register_blueprint(commands_blueprints)
    return app




