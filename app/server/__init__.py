from flask import Blueprint

app_blueprints = Blueprint('app', __name__)

from app.server import routes
