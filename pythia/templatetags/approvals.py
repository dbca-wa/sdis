"""Templatetags for document approval workflows."""

from django import template
from django.core.urlresolvers import reverse

import logging

logger = logging.getLogger(__name__)
register = template.Library()


@register.assignment_tag(takes_context=True)
def get_transitions(context, obj):
    """Output a list of transitions that the document can make."""
    o = obj._meta
    choices = []

    for tx in obj.get_available_status_transitions():
        codename = "%s.%s_%s" % (o.app_label, tx.permission, o.model_name)
        user = context['request'].user
        if any([user.has_perm(codename), user.has_perm(codename, obj)]):
            url = reverse('admin:%s_%s_transition' %
                          (o.app_label, o.model_name),
                          args=(obj._get_pk_val(),))
            url += "?transition=%s" % tx.name
            choices.append({'url': url, 'transition': tx, 'name': tx.name})

    return choices
