"""Provide request.user to Audit's save as modifier."""
from __future__ import (division, print_function, unicode_literals,
                        absolute_import)
from new import instancemethod
from django.conf import settings
USER_ATTR_NAME = getattr(settings, 'LOCAL_USER_ATTR_NAME', '_current_user')

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local
_thread_locals = local()


def _do_set_current_user(user_fun):
    setattr(_thread_locals, USER_ATTR_NAME,
            instancemethod(user_fun, _thread_locals, type(_thread_locals)))


def _set_current_user(user=None):
    """Set current user in local thread.

    Can be used as a hook when request object is not available.
    """
    _do_set_current_user(lambda self: user)


class LocalUserMiddleware(object):
    def process_request(self, request):
        _do_set_current_user(lambda self: getattr(request, 'user', None))


def get_current_user():
    current_user = getattr(_thread_locals, USER_ATTR_NAME, None)
    return current_user() if current_user else current_user
