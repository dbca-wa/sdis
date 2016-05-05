"""Templatetags for document approval workflows."""

from django import template
from django.core.urlresolvers import reverse

import logging

logger = logging.getLogger(__name__)
register = template.Library()

@register.assignment_tag(takes_context=True)
def get_transitions(context, obj):
    """Output a list of transitions that the document can make.

    We are using custom, one-verb permissions on transitions (e.g. "submit"),
    and reconstruct the fully qualified permission name (e.g.
    "documents.submit_conceptplan") here. This allows us to inherit transitions
    through the polymorphic models.

    If we used get_available_user_status_transitions(user) here, we'd have to
    instantiate each transition on each model with the explicit permission set.
    """
    o = obj._meta
    choices = []
    u = context['request'].user
    # for tx in obj.get_available_user_status_transitions(u):
    for tx in obj.get_available_status_transitions():
        codename = "%s.%s_%s" % (o.app_label, tx.permission, o.model_name)
        if any([u.has_perm(codename), u.has_perm(codename, obj)]):
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
