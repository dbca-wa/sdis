"""Provide request.user or superuser to Audit's save() as modifier.

Originally provided (mixed with other code) by django-swingers' middleware,
this middleware is modified from http://stackoverflow.com/questions/2006295/
"""
from __future__ import (division, print_function, unicode_literals,
                        absolute_import)
from django.contrib.auth import get_user_model

from threading import local
_thread_locals = local()


def get_first_user():
    """Return the superuser, typically the first user."""
    User = get_user_model()
    return User.objects.first()


def get_current_user():
    """Return the current request user or the superuser."""
    return getattr(_thread_locals, 'user', get_first_user())


class ThreadLocals(object):
    """Middleware writing variables to thread.local storage.

    Provided variables:

        * user: the request.user (if thread is a request) or superuser
    """

    def process_request(self, request):
        """Attach the request user to thread local storage, default: admin."""
        request_user = getattr(request, 'user', None)
        user_is_anon = request_user and request_user.is_anonymous()
        if request_user and not user_is_anon:
            user = request_user
        else:
            user = get_first_user()
        _thread_locals.user = user
