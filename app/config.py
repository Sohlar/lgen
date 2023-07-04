import os
from dotenv import load_dotenv
import redis
from urllib.parse import urlparse, urlunparse

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    url = urlparse(os.environ.get('DATABASE_URL'))
    #url = url._replace(scheme=url.scheme.replace('postgres', 'postgresql'))
    SQLALCHEMY_DATABASE_URI = urlunparse(url)
    #or \    f"sqlite:///{os.path.join(basedir, 'app.db')}"
    CELERY = {'BROKER_URL': os.environ['REDIS_TLS_URL'],
              'RESULT_BACKEND' : os.environ['REDIS_TLS_URL']}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
"""
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    pass

 class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'test.db')}"
 """