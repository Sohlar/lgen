from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config
from flask_migrate import Migrate
from flask_talisman import Talisman
from celery import Celery
import os
from urllib.parse import quote_plus


db = SQLAlchemy()
login_manager = LoginManager()
celery = Celery()

def create_app(config_class=Config):
    print(os.environ.get('DATABASE_URL'))
    app = Flask(__name__)
    app.config.from_object(config_class)
    talisman = Talisman(app)
    celery = make_celery(app)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    from app.main import main_bp
    app.register_blueprint(main_bp)

    migrate = Migrate(app, db)

    return app

def make_celery(app):

    redis_url = app.config['CELERY_BROKER_URL']
    ssl_cert_reqs = 'required'

    redis_url += '?ssl_cert_reqs=' + quote_plus(ssl_cert_reqs)
    celery = Celery(
        app.import_name,
        broker=redis_url, 
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    print(celery)

    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery