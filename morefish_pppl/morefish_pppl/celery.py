# # path/to/your/proj/src/cfehome/celery.py
# from __future__ import absolute_import, unicode_literals
# import os
# # import traceback
# from celery import Celery
# import logging
# from celery.schedules import crontab
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'morefish_pppl.settings')
#
# app = Celery('morefish_pppl')
#
# # Using a string here means the worker don't have to serialize
# # the configuration object to child processes.
# # - namespace='CELERY' means all celery-related configuration keys
# #   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.timezone = 'UTC'
# # Load task modules from all registered Django app configs.
# app.autodiscover_tasks()
#
#
# # Disable Celery logger
# # logging.getLogger("celery").propagate = False
# # app.config_from_object("dmaiot.celeryconfig")
# # We used CELERY_BROKER_URL in settings.py instead of:
# # app.conf.broker_url = ''
#
# # We used CELERY_BEAT_SCHEDULER in settings.py instead of:
# # app.conf.beat_scheduler = ''django_celery_beat.schedulers.DatabaseScheduler'
# # @app.task(bind=True)
# # def debug_task(self):
# #     print('Request: {0!r}'.format(self.request))
# from kombu import Exchange, Queue
#
# # Define the exchange
# device_task_exchange = Exchange('device_task_queue', type='direct')
#
# # Define the queue
# device_task_queue = Queue('device_task_queue', device_task_exchange, routing_key='device_task_queue')
#
#
# # CELERY ROUTES
# CELERY_ROUTES = {
#     'device.tasks.save_device_data': {'queue': 'device_task_queue'},
#     'notification.tasks.send_threshold_notification': {'queue': 'notification_queue'},
# }
#
#
# CELERY_BEAT_SCHEDULE = {
#     'get-weather-report': {
#         'task': 'tasks.get_weather_report',
#         'schedule': 60,  # Run every 60 seconds (adjust as needed)
#     },
# }



from __future__ import absolute_import, unicode_literals
import os
import logging
from celery import Celery
from kombu import Exchange, Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'morefish_pppl.settings')

app = Celery('morefish_pppl')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.timezone = 'UTC'

# Logging setup
logger = logging.getLogger('celery')
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

# Queues
device_task_exchange = Exchange('device_task_queue', type='direct')
device_task_queue = Queue('device_task_queue', device_task_exchange, routing_key='device_task_queue')
app.conf.task_queues = [device_task_queue]

# Task routes
app.conf.task_routes = {
    'device.tasks.save_device_data': {'queue': 'device_task_queue'},
    'notification.tasks.send_threshold_notification': {'queue': 'notification_queue'},
}

# Beat schedule
app.conf.beat_schedule = {
    'get-weather-report': {
        'task': 'tasks.get_weather_report',
        'schedule': 60,  # every 60 seconds
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
