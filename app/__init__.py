from flask import Flask
from app.config import Config
import os
from urllib.parse import quote_plus
from .extensions import db, login_manager, migrate, celery
from flask_talisman import Talisman

def create_app(config_class=Config):
    print(os.environ.get('DATABASE_URL'))
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    csp = {
        'default-src': [
            '\'self\''
        ],
        'script-src': [
            '\'self\'',
            'https://cdnjs.cloudflare.com',
            'https://cdn.jsdelivr.net',
            'https://code.jquery.com',
            'https://cdn.startbootstrap.com'  
        ],
        'style-src': [
            '\'self\'',
            'https://fonts.googleapis.com',
            'https://code.jquery.com',
            'https://cdnjs.cloudflare.com',
            'https://cdn.jsdelivr.net',
            '\'unsafe-inline\''
        ],
        'font-src': [
            '\'self\'',
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
            'https://cdnjs.cloudflare.com',
            'https://cdn.jsdelivr.net'
        ]
    }
    talisman = Talisman(app, content_security_policy=csp)

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
