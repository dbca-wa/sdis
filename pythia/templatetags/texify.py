"""Templatetags for Latex markup."""
from django.template.defaultfilters import stringfilter, register
from django.utils.safestring import mark_safe
import pypandoc

REPLACEMENTS = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '<': r'\textless{}',
    '>': r'\textgreater',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum',
    '\n': r'\newline ',
    '\r': r'',
    }

COLOURUPS = {
    "1": "success",
    "2": "success",
    "3": "warning",
    "4": "warning",
    "5": "error",
    "6": "error",
    "Rare": "success",
    "Unlikely": "success",
    "Possible": "warning",
    "Likely": "error",
    "Almost Certain": "error"
    }


@register.filter
@stringfilter
def texify(value):
    """Escape special LaTeX characters."""
    for k, v in REPLACEMENTS.items():
        value = value.replace(k, v)
    return mark_safe(value)


@register.filter
@stringfilter
def colourise(value):
    """Colour standard words. If no color, defaults to Fuchsia."""
    return mark_safe(
        r"\textcolor{" + COLOURUPS.get(value, "purple") + "}{" + value + "}")


@register.filter
@stringfilter
def html2latex(value):
    """Convert an HTML string to a Latex string."""
    return mark_safe(pypandoc.convert(value, 'tex', format='html'))
