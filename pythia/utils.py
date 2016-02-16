from __future__ import unicode_literals

import datetime
import os
import subprocess

from bs4 import BeautifulSoup as BS
from bs4.element import NavigableString as NS
from html2text import HTML2Text
import json
import markdown

from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from django.conf import settings

import logging
logger = logging.getLogger(__name__)

def mail_from_template(subject, recipients, template_basename, context):
    #template_html = get_template('{0}.html'.format(template_basename))
    template_text = get_template('{0}.txt'.format(template_basename))
    ctx = Context(context)

    for user in recipients:
        target = '"{0}" <{1}>'.format(user.get_full_name(), user.email)
        ctx['user'] = user
        #content_html = template_html.render(ctx)
        content_text = template_text.render(ctx)
        msg = EmailMultiAlternatives(
                '[SDIS] {0}'.format(subject), content_text,
                settings.DEFAULT_FROM_EMAIL, [target])
        #msg.attach_alternative(content_html, "text/html")
        msg.send()

#------------------------------------------------------------------------------#
# HTML, Markdown, TinyMCE HTML WYSIWYG to markdown in database text fields
#
def text2html(value):
    extensions = ["nl2br", "pythia.md_ext.superscript",
                  "pythia.md_ext.subscript"]
    return mark_safe(markdown.markdown(force_unicode(value), extensions))
                                    #safe_mode=True, enable_attributes=False))

class PythiaHTML2Text(HTML2Text):
    def __init__(self, *args, **kwargs):
        HTML2Text.__init__(self, *args, **kwargs)
        self.body_width = 0   # disable line wraps at 78 chars when saving HTML

    def handle_tag(self, tag, attrs, start):
        if tag == "sub" and not self.ignore_emphasis:
            self.o("~")
        if tag == "sup" and not self.ignore_emphasis:
            self.o("^")
        HTML2Text.handle_tag(self, tag, attrs, start)


def html2text(value):
    h = PythiaHTML2Text(baseurl='')
    return h.handle(value) if value else ""


#-----------------------------------------------------------------------------#
# Version information
#
def get_version(version=None):
    "Returns a PEP 386-compliant version number from VERSION."
    if version is None:
        from pythia import VERSION as version
    else:
        assert len(version) == 5
        assert version[3] in ('alpha', 'beta', 'rc', 'final')

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    # | {a|b|c}N - for alpha, beta and rc releases

    parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:parts])

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        git_changeset = get_timestamp()
        if git_changeset:
            sub = '.dev%s' % git_changeset

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return str(main + sub)


def get_git_changeset(format_string):
    """
    Returns a numeric identifier of the latest git changeset.

    The result is the UTC timestamp of the changeset in YYYYMMDDHHMMSS format.
    This value isn't guaranteed to be unique, but collisions are very unlikely,
    so it's sufficient for generating the development version numbers.
    """
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_log = subprocess.Popen(
        'git log --pretty=format:%s --quiet -1 HEAD' % format_string,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=repo_dir, universal_newlines=True)
    return git_log.communicate()[0]


def get_timestamp():
    timestamp = get_git_changeset("%ct")
    try:
        timestamp = datetime.datetime.utcfromtimestamp(int(timestamp))
    except ValueError:
        return None
    return timestamp.strftime('%Y%m%d%H%M%S')


def get_revision_hash():
    return get_git_changeset("%h")

#-----------------------------------------------------------------------------#
# Data migration utils
#

def is_list_of_lists_of_navigable_strings(obj):
    """Returns true if an object is a list of lists of NavigableStrings.

    An example are tables stored in Markdown.
    """
    return (type(obj) == list and
            type(obj[0]) == list and
            type(obj[0][0]) == NS)

def string_startswith_doubleleftbracket(string):
    """Returns true of a given string starts with a double left bracket `[[`
    """
    return string.startswith("[[")

def list2htmltable(some_string):
    '''Returns a JSON 2D array (a list of list of NavigableStrings) as HTML table
    '''
    table_html = '<table style="width:400px;" border="1" cellpadding="2"><tbody>{0}</tbody></table>'
    row_html = '<tr>{0}</tr>'
    cell_html = '<td>{0}</td>'

    try:
        return table_html.format(
            ''.join([row_html.format(
                ''.join([cell_html.format(cell) for cell in row]
            )) for row in json.loads(some_string)]))
    except:
        print("Found non-JSON string {0}".format(some_string))
        return some_string


def extract_md_tables(html_string):
    '''Returns a given HTML string with markdown tables converted to HTML tables.

    Use this method to convert any Markdown table stored in model fields of type
    text to an HTML table while discarding non-table content.

    '''
    pp = [p.contents for p in BS(html_string).find_all('p', text=string_startswith_doubleleftbracket)]
    if len(pp) > 0:
        return ''.join([''.join([list2htmltable(navigablestring) for navigablestring in x]) for x in pp])
    else:
        return html_string

def convert_md_tables(html_string):
    '''Returns a given HTML string with markdown tables converted to HTML tables.

    Use this method to convert any Markdown table stored in model fields of type
    text to an HTML table.

    `@param html_string` an HTML string containing MArkdown tables
    '''
    pp = [p.contents for p in BS(html_string).find_all('p')] # TODO extract all tags
    # TODO convert only md tables, keep the rest
