from django.template.defaultfilters import stringfilter, register
from django.utils.safestring import mark_safe
from django.template import Context, Template

import json
import markdown
import pypandoc

md = markdown.Markdown(None, extensions=['latex'])

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
    "Complete": "success",
    "CBAS Approved": "success",
    "Endorsed": "success",
    "Not Endorsed": "error",
    "Approved": "success",
    "Not Approved": "error",
    "No Ignitions": "muted",
    "Burn open": "muted",
    "Burn closed": "success",
    "Very Low": "success",
    "Low": "success",
    "Medium": "warning",
    "High": "error",
    "Very High": "error",
    "Incomplete": "error",
    "Not Applicable": "muted",
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
    """
    Escapes special LaTeX characters.
    """
    for k, v in REPLACEMENTS.items():
        value = value.replace(k, v)
    return mark_safe(value)


@register.filter
@stringfilter
def colourise(value):
    """
    Colours standard words. If no color, defaults to Fuchsia.
    """
    return mark_safe("".join((r"\textcolor{", COLOURUPS.get(value, "purple"),
                     "}{", value, "}")))


@register.filter
@stringfilter
def md2latex(value):
    """Converts a Markdown string to a Latex string.
    """
    # stupid markdown surrounds the text with <root> and </root> :(
    # but not when values consists only from spaces :( :( :(
    latex = md.convert(value or '')
    if latex.startswith('<root>'):
        latex = latex[6:]
    if latex.endswith('</root>'):
        latex = latex[:-7]
    return mark_safe(latex)


@register.filter
@stringfilter
def html2latex(value):
    """Converts an HTML string to a Latex string.
    """
    return mark_safe(pypandoc.convert(value, 'tex', format='html'))

