#!/bin/bash

# Bash script to bootstrap a Flask project for the "Arena" app.
# This script creates the required directories, files, and boilerplate code.

set -e  # Exit on any error

PROJECT_NAME="arena-app"

# Create project directory
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# Create directories
mkdir -p app/templates app/static app/migrations tests

# Create __init__.py for Flask app
cat > app/__init__.py <<EOL
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
EOL

# Create models.py
cat > app/models.py <<EOL
"""
This file defines the database models for the application.
"""
from . import db

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    metadata = db.Column(db.Text)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file1_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    file2_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=True)

class Ranking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    ties = db.Column(db.Integer, default=0)
EOL

# Create routes.py
cat > app/routes.py <<EOL
"""
This file defines the routes (endpoints) for the application.
"""
from flask import Blueprint, render_template, request, jsonify
from .models import File, Match, Ranking
from .services import get_random_files, update_rankings

arena = Blueprint('arena', __name__)

@arena.route('/')
def index():
    file1, file2 = get_random_files()
    return render_template('arena.html', file1=file1, file2=file2)

@arena.route('/submit_choice', methods=['POST'])
def submit_choice():
    data = request.json
    winner = data.get('winner')
    loser = data.get('loser')
    Match.save_match(winner, loser)
    update_rankings()
    return jsonify({"message": "Choice submitted successfully!"})
EOL

# Create services.py
cat > app/services.py <<EOL
"""
This file contains the business logic of the application.
"""
import random
from .models import File, Match

def get_random_files():
    files = File.query.order_by(func.random()).limit(2).all()
    return files[0], files[1]

def update_rankings():
    matches = Match.query.all()
    # Logic to compute rankings from matches
    pass
EOL

# Create config.py
cat > config.py <<EOL
"""
This file contains application configuration settings.
"""
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///arena.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
EOL

# Create templates/arena.html
cat > app/templates/arena.html <<EOL
"""
This is the HTML template for the arena page.
"""
<!DOCTYPE html>
<html>
<head>
    <title>Arena</title>
</head>
<body>
    <h1>Choose Your Favorite</h1>
    <div>
        <img src="{{ file1.url }}" alt="{{ file1.name }}">
        <button onclick="submitChoice('{{ file1.id }}', '{{ file2.id }}')">Choose</button>
    </div>
    <div>
        <img src="{{ file2.url }}" alt="{{ file2.name }}">
        <button onclick="submitChoice('{{ file2.id }}', '{{ file1.id }}')">Choose</button>
    </div>
</body>
<script>
function submitChoice(winner, loser) {
    fetch('/submit_choice', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({winner, loser})
    }).then(response => response.json()).then(data => {
        alert(data.message);
        location.reload();
    });
}
</script>
</html>
EOL

# Create run.py
cat > run.py <<EOL
"""
This is the entry point to run the application.
"""
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
EOL

# Create requirements.txt
cat > requirements.txt <<EOL
Flask==2.3.3
Flask-SQLAlchemy==3.0.4
EOL

# Create README.md
cat > README.md <<EOL
# Arena App

This is a simple Flask app to compare files from a Wikimedia Commons category.

## Setup

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Run the application:
    ```bash
    python run.py
    ```

3. Access the app at `http://localhost:5000`.

## Directory Structure

- `app/`: Contains the Flask app files.
- `templates/`: HTML templates.
- `static/`: Static files like CSS and JavaScript.
- `tests/`: Unit tests.
- `run.py`: Entry point for running the app.
EOL

# Done
echo "Project setup complete. Navigate to $PROJECT_NAME and start the app!"
