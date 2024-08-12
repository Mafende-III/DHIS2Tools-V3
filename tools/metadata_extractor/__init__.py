# __init__.py for the metadata_extractor module

from flask import Blueprint

# Create a Blueprint for the metadata extractor
metadata_extractor = Blueprint('metadata_extractor', __name__)

# Import routes and any other necessary components
from . import views

def register_blueprint(app):
    """
    Register the metadata_extractor blueprint with the Flask app.

    :param app: The Flask application instance
    """
    app.register_blueprint(metadata_extractor, url_prefix='/metadata_extractor')
