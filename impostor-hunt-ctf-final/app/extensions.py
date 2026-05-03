from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' #'/login'
login_manager.login_message = 'Please login to access the station.'
login_manager.login_message_category = 'warning'