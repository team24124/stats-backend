import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    SQLALCHEMY_DATABASE_URI = os.getenv('Database_URL', 'placeholder_postgres_url')
    SQLALCHEMY_TRACK_MODIFICATIONS = False