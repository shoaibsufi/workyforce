"""
wsgi.py — WSGI (Web Server Gateway Interface) entry point.

This file is used when deploying Django to a production web server like
gunicorn or uWSGI. For local development you use `python manage.py runserver`
instead and never need to touch this file.

WSGI is the standard Python interface between web servers and web apps.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workforce_planner.settings')
application = get_wsgi_application()
