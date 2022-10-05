import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photographer_client_base_management_service.settings')

app = Celery('photographer_client_base_management_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()