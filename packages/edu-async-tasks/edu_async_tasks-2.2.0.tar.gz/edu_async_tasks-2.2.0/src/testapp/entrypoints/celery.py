import os

from celery import (
    Celery,
)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')

app = Celery('app')

# Running the celery worker server
# $ celery --app=testapp.entrypoints.celery:app worker --loglevel=info
app.config_from_object('django.conf:settings')
app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()
