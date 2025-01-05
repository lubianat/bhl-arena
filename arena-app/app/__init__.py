"""
This file initializes the Flask application.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize database
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from .routes import arena
    app.register_blueprint(arena)

    return app
