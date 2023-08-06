""" Module task_manager.
This module used by celery as entrypoint.
Contains configuration of queues, routes and scheduler.
"""
from celery import Celery
from celery.schedules import crontab
from kombu import Queue, Exchange

REDIS_URL = 'redis://localhost:6379/0'

celery_app = Celery('main_celery', broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.task_queues = (
    Queue('high', Exchange('high'), routing_key='high'),
    Queue('normal', Exchange('normal'), routing_key='normal'),
    Queue('low', Exchange('low'), routing_key='low'),
)

celery_app.conf.task_routes = {
    'tasks.data_updater.run_worker': {'queue': 'normal'},
}

celery_app.conf.imports = (
    'tasks.data_updater',
)

celery_app.conf.beat_schedule = {
    'once-per-day': {
        'task': 'tasks.data_updater.run_worker',
        'schedule': crontab(hour='*/12'),
    },
}
