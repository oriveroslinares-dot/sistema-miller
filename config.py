import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'miller-sistema-secreto-2024'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'miller.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
