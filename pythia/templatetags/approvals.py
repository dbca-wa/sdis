"""Templatetags for document approval workflows."""

from django import template
from django.core.urlresolvers import reverse

import logging

logger = logging.getLogger(__name__)
register = template.Library()


@register.assignment_tag(takes_context=True)
def get_transitions(context, obj):
    """Return a list of dicts with allowed transitions.

    Each transition dict contains:

    * url: POST to the transition URL to run this transition
    * transition: the django-fsm transition object
    * name: the tx name as string
    * verbose: the custom  tx property "verbose" with the human readable label
    * notify: the custom tx property "notify", Boolean, whether the email
      notification is selected by default or not (User can untick/tick)
    """
    o = obj._meta
    choices = []
    u = context['request'].user

    for tx in obj.get_available_user_status_transitions(u):
        url = reverse('admin:%s_%s_transition' % (
            o.app_label, o.model_name), args=(obj._get_pk_val(),))
        url += "?transition=%s" % tx.name
        choices.append({'url': url,
                        'transition': tx,
                        'name': tx.name,
                        'verbose': tx.custom["verbose"],
                        'notify': tx.custom["notify"]
                        })

    return choices
