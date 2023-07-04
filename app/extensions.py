from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_talisman import Talisman
from celery import Celery

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
celery = Celery()