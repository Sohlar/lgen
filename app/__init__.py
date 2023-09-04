from flask import Flask
from flask_mail import Mail
from app.config import Config
import os
from urllib.parse import quote_plus
from .extensions import db, login_manager, migrate, celery
from flask_talisman import Talisman


mail = Mail()
def make_celery(app):

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super(ContextTask, self).__call__(*args, **kwargs)

    celery.Task = ContextTask
    from .main.tasks import search_engine_task
    return celery


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)
    
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    make_celery(app)

    csp = {
        'default-src': [
            '\'self\''
        ],
        'script-src': [
            '\'self\'',
            'https://cdnjs.cloudflare.com',
            'https://cdn.jsdelivr.net',
            'https://code.jquery.com',
            'https://cdn.startbootstrap.com',
            'https://js.stripe.com',  
            '\'unsafe-inline\''
        ],
        'script-src-elem': [
            '\'self\'',
            'https://cdnjs.cloudflare.com',
            'https://cdn.jsdelivr.net',
            'https://code.jquery.com',
            'https://cdn.startbootstrap.com',
            'https://js.stripe.com',  
            '\'unsafe-inline\''
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
        ],
        'frame-src': [
            '\'self\'',
            'https://js.stripe.com'  
        ]
    }
    talisman = Talisman(app, content_security_policy=csp)

    from app.main import main_bp
    app.register_blueprint(main_bp)

    return app
