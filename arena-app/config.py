"""
This file contains application configuration settings.
"""
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///arena.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
