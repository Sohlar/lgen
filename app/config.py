import os
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse


load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key"
    STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY")
    url = urlparse(os.environ.get("DATABASE_URL"))
    #url = url._replace(scheme=url.scheme.replace("postgres", "postgresql"))
    SQLALCHEMY_DATABASE_URI = urlunparse(url)
    # or \    f"sqlite:///{os.path.join(basedir, 'app.db')}"

    CELERY = {
        "BROKER_URL": os.environ["REDIS_TLS_URL"] + "?ssl_cert_reqs=CERT_NONE",
        "RESULT_BACKEND": os.environ["REDIS_TLS_URL"] + "?ssl_cert_reqs=CERT_NONE",
    }
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

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
