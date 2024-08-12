import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key')  # Replace with your secret key
    DEBUG = os.environ.get('FLASK_DEBUG', True)
    
    # Flask-Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')  # Replace with your SMTP server
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'your-email@example.com')  # Replace with your email
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your-email-password')  # Replace with your email password
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', False)
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///usage_stats.db')  # SQLite by default
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # DHIS2 settings (optional, for future configurations)
    DHIS2_API_URL = os.environ.get('DHIS2_API_URL', 'https://your-dhis2-url/api')
    DHIS2_USERNAME = os.environ.get('DHIS2_USERNAME', 'your-username')
    DHIS2_PASSWORD = os.environ.get('DHIS2_PASSWORD', 'your-password')

# Ensure to use this config in your Flask app initialization
