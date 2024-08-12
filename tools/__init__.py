from flask import Flask
from flask_mail import Mail
from .metadata_extractor import metadata_extractor as metadata_extractor_blueprint

def create_app():
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__)
    
    # Load configuration from a separate config file or environment variables
    app.config.from_object('config.Config')

    # Initialize Flask-Mail
    mail = Mail(app)
    
    # Register Blueprints
    app.register_blueprint(metadata_extractor_blueprint, url_prefix='/metadata_extractor')
    
    # Additional Blueprints can be registered here
    # app.register_blueprint(other_blueprint, url_prefix='/other_prefix')
    
    # Initialize additional extensions here if needed
    # e.g., db.init_app(app)
    
    return app
