
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance_dashboard.db'
    app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'
    CORS(app)
    JWTManager(app)
    db.init_app(app)

    # Register Blueprints
    from .routes.user_routes import user_bp
    app.register_blueprint(user_bp)

    return app
