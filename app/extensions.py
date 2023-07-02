from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_talisman import Talisman
from celery import Celery

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csp = {
    'default-src': [
        '\'self\''
    ],
    'script-src': [
        'cdnjs.cloudflare.com',
        'cdn.jsdelivr.net'
    ],
    'style-src': [
        'fonts.googleapis.com'
        #'code.jquery.com'
    ]
}


talisman = Talisman(content_security_policy=csp)
celery = Celery()