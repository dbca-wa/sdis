"""Module level utilities for pythia.

This module contains utilities for logging, sending email, displaying code
versions, and superseded Markdown support.
"""
from __future__ import unicode_literals

import datetime
from itertools import chain
# import json
import logging
import os
import subprocess

# from bs4 import BeautifulSoup as BS
# from bs4.element import NavigableString as NS
# from html2text import HTML2Text
# import json
# import markdown

# from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import get_template
# from django.template import Context
# from django.utils.encoding import force_unicode
# from django.utils.safestring import mark_safe
# from guardian.shortcuts import assign_perm

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------#
# String manipulation
def texify_filename(filename):
    """Convert a filename into a Latex-proof name.

    Remove all non-alphanumeric characters, leave extension intact.
    This function is essential to image filenames used in Latex templates,
    as some non-alphanumeric characters have special meaning in Latex.
    """
    fn, ext = os.path.splitext(filename)
    fn_clean = filter(str.isalnum, str(fn))

    return "{0}{1}".format(fn_clean, ext)


# -----------------------------------------------------------------------------#
# Permissions


def setup_permissions():
    """Create global permissions once-off.

    Create project permissions, which can be assigned per object to teams.
    Create global permissions and assign to Group "Managers".
    """
    managers, created = Group.objects.get_or_create(name='Managers')
    doc_ct = ContentType.objects.filter(app_label='documents')
    proj_ct = ContentType.objects.filter(app_label='projects')

    for content_type in list(chain(doc_ct, proj_ct)):
        codename = "manage_%s" % (content_type.model)

        p, created = Permission.objects.get_or_create(
            content_type=content_type, codename=codename,
            name="Can manage %s" % (content_type.name))

        managers.permissions.add(p)
        logger.debug("Granted {0} to Group managers".format(p))


# -----------------------------------------------------------------------------#
# HTML, Markdown, TinyMCE HTML WYSIWYG to markdown in database text fields
#


# def text2html(value):
#     """Convert a Markdown string to HTML."""
#     extensions = ["nl2br",
#                   "pythia.md_ext.superscript",
#                   "pythia.md_ext.subscript",
#                   ]
#     return mark_safe(markdown.markdown(force_unicode(value), extensions))
#
#
# class PythiaHTML2Text(HTML2Text):
#     """Markdown utility class."""
#
#     def __init__(self, *args, **kwargs):
#         """Override init to disable line wraps at 78 chars when saving HTML."""  # noqa
#         HTML2Text.__init__(self, *args, **kwargs)
#         self.body_width = 0
#
#     def handle_tag(self, tag, attrs, start):
#         """Provide handle_tag method."""
#         if tag == "sub" and not self.ignore_emphasis:
#             self.o("~")
#         if tag == "sup" and not self.ignore_emphasis:
#             self.o("^")
#         HTML2Text.handle_tag(self, tag, attrs, start)
#
#
# def html2text(value):
#     """Return html2text."""
#     h = PythiaHTML2Text(baseurl='')
#     return h.handle(value) if value else ""


# -----------------------------------------------------------------------------#
# Version information


def get_version(version=None):
    """Return a PEP 386-compliant version number from VERSION."""
    if version is None:
        from pythia import VERSION as version  # noqa
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
    """Return a numeric identifier of the latest git changeset.

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
    """Return a URL-safe, spaceless string of date and time."""
    timestamp = get_git_changeset("%ct")
    try:
        timestamp = datetime.datetime.utcfromtimestamp(int(timestamp))
    except ValueError:
        return None
    return timestamp.strftime('%Y%m%d%H%M%S')


def get_revision_hash():
    """Return a URL-safe Git revision hash."""
    return get_git_changeset("%h")

# -----------------------------------------------------------------------------#
# Data migration utils

#
# def is_list_of_lists_of_navigable_strings(obj):
#     """Return true if an object is a list of lists of NavigableStrings.
#
#     An example are tables stored in Markdown.
#     """
#     return (type(obj) == list and
#             type(obj[0]) == list and
#             type(obj[0][0]) == NS)
#
#
# def string_startswith_doubleleftbracket(string):
#     """Returns true of a given string starts with a double left bracket `[[`
#     """
#     return string.startswith("[[")
#
#
# def list2htmltable(some_string):
#     '''Return a JSON 2D array (a list of list of NavigableStrings) as HTML table.'''  # noqa
#
#     table_html = '<table style="width:400px;" border="1" ' +\
#                  'cellpadding="2"><tbody>{0}</tbody></table>'
#     row_html = '<tr>{0}</tr>'
#     cell_html = '<td>{0}</td>'
#
#     try:
#         return table_html.format(
#             ''.join([row_html.format(
#                 ''.join([cell_html.format(cell) for cell in row]
#                         )) for row in json.loads(some_string)]))
#     except:
#         logger.warning("Found non-JSON string {0}".format(some_string))
#         return some_string
#
#
# def extract_md_tables(html_string):
#     '''Return a given HTML string with markdown tables converted to HTML tables.  # noqa
#
#     Use this method to convert any Markdown table stored in model fields of
#     type text to an HTML table while discarding non-table content.
#
#     '''
#     pp = [p.contents for p in BS(html_string).find_all(
#         'p', text=string_startswith_doubleleftbracket)]
#     if len(pp) > 0:
#         return ''.join([''.join(
#             [list2htmltable(navigablestring) for navigablestring in x]) for x
#                         in pp])
#     else:
#         return html_string
#
#
# def convert_md_tables(html_string):
#     '''Return a given HTML string with markdown tables converted to HTML tables. # noqa
#
#     Use this method to convert any Markdown table stored in model fields of
#     type text to an HTML table.
#
#     `@param html_string` an HTML string containing MArkdown tables
#     '''
#     # pp = [p.contents for p in BS(html_string).find_all('p')]
#     # TODO extract all tags
#     # TODO convert only md tables, keep the rest
#     logger.warning("Not implemented: pythia.utils.convert_md_tables")
