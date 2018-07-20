"""Provide request.user or superuser to Audit's save() as modifier.

Originally provided (mixed with other code) by django-swingers' middleware,
this middleware is modified from http://stackoverflow.com/questions/2006295/
"""
from __future__ import (division, print_function, unicode_literals,
                        absolute_import)
from django import http
from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.db.models import signals
from django.utils.functional import curry

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


class SSOLoginMiddleware(object):

    def process_request(self, request):
        User = get_user_model()
        if request.path.startswith('/logout') and "HTTP_X_LOGOUT_URL" in request.META:
            logout(request)
            return http.HttpResponseRedirect(request.META["HTTP_X_LOGOUT_URL"])
        if not request.user.is_authenticated() and "HTTP_REMOTE_USER" in request.META:
            attributemap = {
                "username": "HTTP_REMOTE_USER",
                "last_name": "HTTP_X_LAST_NAME",
                "first_name": "HTTP_X_FIRST_NAME",
                "email": "HTTP_X_EMAIL",
            }

            for key, value in attributemap.iteritems():
                attributemap[key] = request.META[value]

            if hasattr(settings, "ALLOWED_EMAIL_SUFFIXES") and settings.ALLOWED_EMAIL_SUFFIXES:
                allowed = settings.ALLOWED_EMAIL_SUFFIXES
                if isinstance(settings.ALLOWED_EMAIL_SUFFIXES, basestring):
                    allowed = [settings.ALLOWED_EMAIL_SUFFIXES]
                if not any([attributemap["email"].lower().endswith(x) for x in allowed]):
                    return http.HttpResponseForbidden()

            if attributemap["email"] and User.objects.filter(email__istartswith=attributemap["email"]).exists():
                user = User.objects.get(email__istartswith=attributemap["email"])
            elif User.objects.filter(username__iexact=attributemap["username"]).exists():
                user = User.objects.get(username__iexact=attributemap["username"])
            else:
                user = User()
            user.__dict__.update(attributemap)
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)


class AuditMiddleware(object):
    """Adds creator and modifier foreign key refs to any model automatically.
    Ref: https://gist.github.com/mindlace/3918300
    """

    def process_request(self, request):
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user = request.user
            else:
                user = None

            set_auditfields = curry(self.set_auditfields, user)
            signals.pre_save.connect(set_auditfields, dispatch_uid=(self.__class__, request,), weak=False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        return response

    def set_auditfields(self, user, sender, instance, **kwargs):
        if not getattr(instance, 'creator_id', None):
            instance.creator = user
        if hasattr(instance, 'modifier_id'):
            instance.modifier = user
