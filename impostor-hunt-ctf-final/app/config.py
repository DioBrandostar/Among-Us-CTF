import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Helper function to get the correct path for the database file
def get_db_path():
    # If running as an executable, place the DB in the same directory as the executable
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        return f"sqlite:///{os.path.join(base_dir, 'impostor_hunt.db')}"
    # Otherwise, use the default relative path
    return 'sqlite:///impostor_hunt.db'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', get_db_path())
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    WTF_CSRF_ENABLED = True

config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig 
}