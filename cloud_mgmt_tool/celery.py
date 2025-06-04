# cloud_mgmt/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_mgmt.settings')

app = Celery('cloud_mgmt_tool')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
