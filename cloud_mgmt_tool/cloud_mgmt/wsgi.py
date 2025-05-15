"""
WSGI config for cloud_mgmt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# point at the real location of your settings.py:
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'cloud_mgmt_tool.cloud_mgmt.settings'
)

application = get_wsgi_application()
