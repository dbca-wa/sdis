"""
WSGI config for sdis project.

It exposes the WSGI callable as a module-level variable named ``application``.

@see https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
@see https://github.com/kennethreitz/dj-static
@see http://django-confy.readthedocs.org/en/latest/usage.html
"""

import confy
from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling

confy.read_environment_file()
application = Cling(MediaCling(get_wsgi_application()))

