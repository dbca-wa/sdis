from django import template
from django.core.urlresolvers import reverse

import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_transitions(context, obj):
    """
    Output a list of transitions that the document can make.
    """
    opts = obj._meta
    choices = []

    for transition, method in obj.get_available_status_transitions():
        codename = "%s.%s_%s" % (opts.app_label, method.permission,
            opts.model_name)
        user = context['request'].user
        if any([user.has_perm(codename), user.has_perm(codename, obj)]):
            url = reverse('admin:%s_%s_transition' %
                          (opts.app_label, opts.model_name),
                          args=(obj._get_pk_val(),))
            url += "?transition=%s" % transition
            choices.append({
                'url': url,
                'transition': transition,
                'name': method.verbose_name
            })

    return choices
