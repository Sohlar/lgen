from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_talisman import Talisman
from celery import Celery
from .config import Config
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
celery = Celery(broker=Config.CELERY['BROKER_URL'], backend=Config.CELERY['RESULT_BACKEND'])
mail = Mail()
