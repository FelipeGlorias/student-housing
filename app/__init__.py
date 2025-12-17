# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

# Flask-Login config
login_manager.login_view = 'auth.login'  # Redirects for @login_required
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    
    # Basic config
    app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a strong key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Import models here so that User is available for user_loader
    from app.models import User

    # Flask-Login user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from app.routes import main
    from app.auth import auth
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')

    return app
