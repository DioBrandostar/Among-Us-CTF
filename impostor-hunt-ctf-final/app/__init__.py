import os
from flask import Flask
from app.extensions import db, login_manager
from app.config import config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))
    
    # Secret key for sessions
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'horizon-7-secret-key-change-me')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access the station.'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = 'strong'  # Add this

    # Import models to register them
    from app import models
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.emergency import emergency_bp
    from app.routes.scoreboard import scoreboard_bp
    from app.routes.rooms.electrical import electrical_bp
    from app.routes.rooms.cafeteria import cafeteria_bp
    from app.routes.rooms.medbay import medbay_bp
    from app.routes.rooms.security import security_bp
    from app.routes.rooms.communications import communications_bp
    from app.routes.rooms.reactor import reactor_bp
    from app.routes.rooms.admin_terminal import admin_terminal_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(emergency_bp)
    app.register_blueprint(scoreboard_bp)
    app.register_blueprint(electrical_bp)
    app.register_blueprint(cafeteria_bp)
    app.register_blueprint(medbay_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(communications_bp)
    app.register_blueprint(reactor_bp)
    app.register_blueprint(admin_terminal_bp)

    with app.app_context():
        db.create_all()

    return app