import os
from dotenv import load_dotenv
import redis
from urllib.parse import urlparse

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(basedir, 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    CELERY_BROKER_URL = os.environ.get('REDIS_TLS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_TLS_URL')
"""
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    pass

 class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'test.db')}"
 """