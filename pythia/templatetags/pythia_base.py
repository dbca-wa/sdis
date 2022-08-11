import json

import django
from django.conf import settings
from django.contrib.admin.util import lookup_field, quote
from django.conf import settings
from django.core.urlresolvers import resolve, reverse
from django.utils.encoding import force_str
from django import template

import pythia
from pythia.utils import get_revision_hash

from confy import env
import confy
try:
    confy.read_environment_file(".env")
except:
    pass

register = template.Library()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

@register.filter
def pythia_urlname(value, arg):
    model = value.model_name
    return 'admin:%s_%s_%s' % (value.app_label, model, arg)


@register.filter
def pythia_urlquote(value):
    return quote(value)


@register.filter
def diffurl(versionurl):
    res = resolve(versionurl)
    return reverse(res.view_name.replace('_revision', '_diff'), args=res.args)


@register.inclusion_tag("admin/pythia/includes/fieldset.html")
def doccontext(fieldset):
    # it's an iterator :(
    errors = ""
    field_ = None
    help_text = ""
    heading = ""
    for line in fieldset:
        for fieldw in line:
            # stupid django readonly fields :( bleeee
            if getattr(fieldw, 'is_readonly', False):
                field, obj, model_admin = (fieldw.field['field'],
                                           fieldw.form.instance,
                                           fieldw.model_admin)
                f, attr, value = lookup_field(field, obj, model_admin)
                if fieldw.field['name'].lower() == "help_text":
                    help_text = value
                elif fieldw.field['name'].lower() == "heading":
                    heading = value
            else:
                if fieldw.field.name.lower() == "context":
                    field_ = fieldw.field
                    errors = field_.errors
                    field_.allow_tags = True

    return {'classes': fieldset.classes,
            'errors': errors,
            'heading': heading,
            'field': field_,
            'help_text': help_text}


@register.inclusion_tag('admin/google_analytics.html', takes_context=True)
def google_analytics(context):
    """Return the GA tracking code JS snippet with a key from settings."""
    context['GOOGLE_ANALYTICS_KEY'] = settings.GOOGLE_ANALYTICS_KEY
    return context


@register.simple_tag
def google_analytics_key():
    """Return the GA tracking code key from .env via settings."""
    return settings.GOOGLE_ANALYTICS_KEY


@register.inclusion_tag('admin/submit_line.html', takes_context=True)
def submit_widgets(context):
    """Display the row of buttons for delete and save."""
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']

    ctx = {
        'opts': opts,
        'show_delete_link': (not is_popup and
                             context['has_delete_permission'] and
                             change and context.get('show_delete', True)),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': context['has_add_permission'] and
        not is_popup and (not save_as or context['add']),
        'show_save_and_continue': (not is_popup and
                                   context['has_change_permission']),
        'is_popup': is_popup,
        'show_save': True,
        'preserved_filters': context.get('preserved_filters'),
        'current': context.get('current'),
        'title': context.get('title'),
        }
    if context.get('original') is not None:
        ctx['original'] = context['original']
    return ctx


@register.inclusion_tag('admin/pythia/ararreport/includes/as_html.html')
def as_html(original, field, tag='h1'):
    text = getattr(original, field)
    heading = force_str(original._meta.get_field(field).verbose_name)
    return {
        'original': original,
        'text': text,
        'heading': heading,
        'opts': original._meta,
        'tag': tag,
        'anchor': "{0}:{1}.{2}".format(
            original.opts.module_name, original.pk, field), }


@register.simple_tag
def get_version_info():
    return "%(name)s %(version)s, Django %(django)s" % {
        'name': env("SITE_NAME", default="SPMS"),
        'version': env("SDIS_RELEASE", default="5.0.0"),
        'django': django.get_version()}


@register.inclusion_tag('latex/includes/as_latex.tex')
def as_latex(original, field, tag='section', show_heading=True):
    """Render a text field as Latex paragraph with heading."""
    text = getattr(original, field)
    heading = force_str(original._meta.get_field(field).verbose_name)
    return {
        'original': original,
        'text': text,
        'heading': heading,
        'opts': original._meta,
        'tag': tag,
        'show_heading': show_heading}


@register.inclusion_tag('latex/includes/as_latex_table.tex')
def as_latex_table(original, field, tag='section'):
    """Converts a string of list of lists from a PythiaArrayField
    to a Latex table string.
    """
    text = json.loads(getattr(original, field))
    heading = force_str(original._meta.get_field(field).verbose_name)
    col = "| " + "".join(" X |"*len(text[0]))
    return {
        'original': original,
        'text': text,
        'heading': heading,
        'opts': original._meta,
        'tag': tag,
        'col': col, }


@register.inclusion_tag('users/portfolio.html')
def user_portfolio(usr, personalise=True):
    """A templatetag to render a Tasks / Portfolio list for a given User.

    The tag requires the outputs of the workhorse functions ``User.tasklist()``
    and ``User.portfolio()`` which run optimised db queries to retrieve tasks
    (documents requiring the User's attention) and portfolio (projects in which
    the User participates).

    The template can be personalised to address the user directly as "You",
    "My", etc. or render the user's first name.

    show_docs: https://github.com/dbca-wa/sdis/issues/184
    """
    return {'my_tasklist': usr.tasklist,
            'my_portfolio': usr.portfolio,
            'my': "my" if personalise else "{0}'s".format(force_str(usr.first_name)),
            'you': "you" if personalise else usr.first_name,
            's': "" if personalise else "s",
            'are': "are" if personalise else "is",
            'your': "your" if personalise else "{0}'s".format(force_str(usr.first_name)), 
            'show_docs': usr.show_docs,
            }


@register.inclusion_tag('frontpage/scmt_preread.html')
def scmt_preread():
    """Return all documents that will be discussed at the next BCS SCMT meeting.

    Relevant documents are ConceptPlans and ProjectClosures "in approval" of Division BCS.
    """
    from pythia.documents.models import (Document, ConceptPlan, ProjectClosure)

    # SCP, PCF "in approval" of Division BCS
    scp = ConceptPlan.objects.filter(
        status=Document.STATUS_INAPPROVAL, 
        project__program__division__slug__iexact="BCS")

    pcf = ProjectClosure.objects.filter(
        status=Document.STATUS_INAPPROVAL, 
        project__program__division__slug__iexact="BCS")

    return {"conceptplans": list(scp),
            "projectclosures": list(pcf),
            "length": len(scp) + len(pcf), }
