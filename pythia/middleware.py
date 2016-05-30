"""Provide request.user to Audit's save as modifier.

Originally provided (mixed with other code) by django-swingers' auth middleware
Modified from http://stackoverflow.com/questions/2006295/
"""
from __future__ import (division, print_function, unicode_literals,
                        absolute_import)
from django.conf import settings
from django.contrib.auth import get_user_model
USER_ATTR_NAME = getattr(settings, 'LOCAL_USER_ATTR_NAME', '_current_user')


try:
    from threading import local
except ImportError:
    # Python 2.3 compatibility
    from django.utils._threading_local import local

_thread_locals = local()

def get_first_user():
    """Return the superuser."""
    User = get_user_model()
    return User.objects.first()


def get_current_user():
    """Return the current request user or the superuser."""
    return getattr(_thread_locals, 'user', get_first_user())


class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""

    def process_request(self, request):
        """Attach the request user to thread local storage, default: admin."""
        request_user = getattr(request, 'user', None)
        user_is_anon = request_user and request_user.is_anonymous()
        # print("Request has user {0}, anonymous: {1}".format(
        #     request_user, user_is_anon))
        if request_user and not user_is_anon:
            user = request_user
        else:
            user = get_first_user()
        _thread_locals.user = user
