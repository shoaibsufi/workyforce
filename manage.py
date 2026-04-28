#!/usr/bin/env python
"""
manage.py — Django's command-line utility.

This is the script you run to do almost everything in Django:

  python manage.py runserver       — start the development web server
  python manage.py migrate         — create/update database tables from models
  python manage.py makemigrations  — detect model changes and create migration files
  python manage.py createsuperuser — create an admin account
  python manage.py shell           — open a Python shell with Django loaded
  python manage.py import_spreadsheet — our custom command to load the Excel data

You'll use this file constantly. It simply points Django at our settings module
and then hands off to Django's own management infrastructure.
"""

import os
import sys


def main():
    """Run administrative tasks."""
    # Tell Django which settings file to use.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workforce_planner.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
