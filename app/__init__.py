from flask import Flask
from app.config import Config
import os
from urllib.parse import quote_plus
from .extensions import db, login_manager, migrate, talisman, celery

def create_app(config_class=Config):
    print(os.environ.get('DATABASE_URL'))
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    talisman.init_app(app)

    celery.conf.update(app.config['CELERY'])

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super(ContextTask, self).__call__(*args, **kwargs)

    celery.Task = ContextTask

    from app.main import main_bp
    app.register_blueprint(main_bp)

    return app
