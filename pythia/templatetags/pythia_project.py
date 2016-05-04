from django import template
from django.db.models import Max
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter
@stringfilter
def latex_criteria(value):
    """
    Priority justification criteria in A4 latex PDF
    """
    value = value.replace('    ', '\hspace*{0.5cm}').replace('\n', '\\newline')
    return value
