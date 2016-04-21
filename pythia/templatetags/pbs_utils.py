from django.conf import settings
from django.shortcuts import resolve_url
from django import template


register = template.Library()


@register.simple_tag
def login_url():
    return resolve_url(settings.LOGIN_URL)
