web: gunicorn run:app --workers 4
worker: celery -A celery_worker:celery worker --pool=threads --loglevel=debug 
