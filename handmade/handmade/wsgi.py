"""
WSGI config for handmade project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys
import traceback

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'handmade.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    raise e

if os.environ.get('DEBUG', False):
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
