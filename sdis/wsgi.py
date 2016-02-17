"""
WSGI config for sdis project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""
import confy
from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling

confy.read_environment_file()
application = Cling(MediaCling(get_wsgi_application()))
