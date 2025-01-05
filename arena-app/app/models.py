"""
This file defines the database models for the application.
"""
from . import db

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    elo = db.Column(db.Float, default=1200)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)

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
