import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


app = Celery(broker=settings.CELERY_BROKER_URL)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS)
app.conf.beat_schedule = {
    'update_items_and_workflows_task': {
        'task': 'update_items_and_workflows_task',
        'schedule': crontab(minute='*/1'),
        'args': (),
    },
}
app.conf.timezone = 'UTC'

if __name__ == '__main__':
    app.start()
