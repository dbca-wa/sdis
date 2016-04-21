import markdown

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def markdownify(value):
    extensions = ["nl2br", "pythia.md_ext.superscript",
                  "pythia.md_ext.subscript"]
    return mark_safe(markdown.markdown(force_unicode(value), extensions))
    # safe_mode=True, enable_attributes=False))
