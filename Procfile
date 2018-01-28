web: gunicorn cpython_stats.__main__:app
worker: celery beat --app=cpython_stats.worker --loglevel=debug
