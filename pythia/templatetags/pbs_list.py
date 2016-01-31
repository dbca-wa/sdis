from django import template
from django.contrib.admin.templatetags.admin_list import result_hidden_fields
from django.contrib.admin.views.main import PAGE_VAR
from django.utils.encoding import force_text, smart_str
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.admin.utils import (lookup_field, display_for_field,
                                       display_for_value, label_for_field)
from django.contrib.admin.views.main import (EMPTY_CHANGELIST_VALUE,
                                             ORDER_VAR)
from django.db import models

import datetime
import json
import re

from swingers.utils import shorthash


register = template.Library()

DOT = '.'


@register.simple_tag
def aggregate_sum(queryset, fieldname):
    return queryset.aggregate(models.Sum(fieldname))[fieldname + "__sum"]


@register.simple_tag
def paginator_number(cl, i):
    """
    Generates an individual page index link in a paginated list.
    """
    if i == DOT:
        return '<li class="disabled"><a href="#" onclick="return false;">..' \
               '.</a></li>'
    elif i == cl.page_num:
        return format_html(
            '<li class="active"><a href="">%d</a></li> ' % (i + 1))
    else:
        return format_html(
            '<li><a href="%s"%s>%d</a></li> ' % (
                cl.get_query_string({PAGE_VAR: i}),
                mark_safe(' class="end"'
                          if i == cl.paginator.num_pages - 1 else ''),
                i + 1)
        )


@register.simple_tag
def dump_json(obj):
    """
    Retrieves constant name from given object returns JSON
    """
    return format_html(json.dumps(obj))


class SetVarNode(template.Node):
    def __init__(self, new_val, var_name):
        self.new_val = new_val
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = self.new_val
        return ''


@register.tag
def setvar(parser, token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    new_val, var_name = m.groups()
    if not (new_val[0] == new_val[-1] and new_val[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return SetVarNode(new_val[1:-1], var_name)


class ResultList(list):
    def __init__(self, form, group, previous, *items):
        self.form = form
        self.group = group
        self.previous = previous
        self.group_id = "group-{0}".format(shorthash(group))
        super(ResultList, self).__init__(*items)


def name_for_group(group_name, cl, res):
    """
    Allow a customised ModelAdmin to specify a new field `list_group_by`
    that can be a method on the model admin or the model itself that defines
    group ordering.
    """
    if hasattr(cl.model_admin, 'list_group_by'):
        if callable(group_name):
            group = group_name(res)
        else:
            group = getattr(res, cl.model_admin.list_group_by, None)
    else:
        group = None
    return group


def result_headers(cl):
    """
    Generates the list column headers.
    """
    ordering_field_columns = cl.get_ordering_field_columns()
    for i, field_name in enumerate(cl.list_display):
        text, attr = label_for_field(field_name, cl.model,
                                     model_admin=cl.model_admin,
                                     return_attr=True)
        th_classes = []
        # Append "required" class to fields in model._required_fields
        if (hasattr(cl.model_admin.model, '_required_fields') and
                field_name in getattr(cl.model_admin.model,
                                      '_required_fields')):
            th_classes.append("required")
        if attr:
            # Potentially not sortable

            # Check custom field for required=True
            if hasattr(attr, "required") and attr.required:
                th_classes.append("required")

            # if the field is the action checkbox: no sorting and special class
            if field_name == 'action_checkbox':
                yield {
                    "text": text,
                    "classes": 'action-checkbox-column',
                    "sortable": False,
                }
                continue

            admin_order_field = getattr(attr, "admin_order_field", None)
            if not admin_order_field:
                # Not sortable
                yield {
                    "text": text,
                    "sortable": False,
                    "column": 'column-%s' % field_name,
                }
                continue

        # OK, it is sortable if we got this far
        order_type = ''
        new_order_type = 'asc'
        sort_priority = 0
        sorted = False
        # Is it currently being sorted on?
        if i in ordering_field_columns:
            sorted = True
            order_type = ordering_field_columns.get(i).lower()
            sort_priority = list(ordering_field_columns).index(i) + 1
            th_classes.append('sorted %sending' % order_type)
            new_order_type = {'asc': 'desc', 'desc': 'asc'}[order_type]

        # build new ordering param
        o_list_primary = []  # URL for making this field the primary sort
        o_list_remove = []  # URL for removing this field from sort
        o_list_toggle = []  # URL for toggling order type for this field
        make_qs_param = lambda t, n: ('-' if t == 'desc' else '') + str(n)

        for j, ot in ordering_field_columns.items():
            if j == i:  # Same column
                param = make_qs_param(new_order_type, j)
                # We want clicking on this header to bring the ordering to the
                # front
                o_list_primary.insert(0, param)
                o_list_toggle.append(param)
                # o_list_remove - omit
            else:
                param = make_qs_param(ot, j)
                o_list_primary.append(param)
                o_list_toggle.append(param)
                o_list_remove.append(param)

        if i not in ordering_field_columns:
            o_list_primary.insert(0, make_qs_param(new_order_type, i))

        yield {
            "text": text,
            "sortable": True,
            "sorted": sorted,
            "ascending": order_type == "asc",
            "sort_priority": sort_priority,
            "url_primary": cl.get_query_string(
                {ORDER_VAR: '.'.join(o_list_primary)}),
            "url_remove": cl.get_query_string(
                {ORDER_VAR: '.'.join(o_list_remove)}),
            "url_toggle": cl.get_query_string(
                {ORDER_VAR: '.'.join(o_list_toggle)}),
            "classes": ' '.join(th_classes) if th_classes else '',
            "column": 'column-%s' % field_name,
        }


def items_for_result(cl, result, form):
    # majority copied from
    # django.contrib.admin.templatetags.admin_list.items_for_result
    # we only customize the order of error fields - error comes after field
    #     result_repr = mark_safe(force_text(bf.errors) + force_text(bf))
    first = True
    pk = cl.lookup_opts.pk.attname
    for field_name in cl.list_display:
        row_classes = ['column-{0}'.format(field_name)]
        try:
            f, attr, value = lookup_field(field_name, result, cl.model_admin)
        except ObjectDoesNotExist:
            result_repr = EMPTY_CHANGELIST_VALUE
        else:
            if f is None:
                if field_name == 'action_checkbox':
                    row_classes.append("action-checkbox")
                allow_tags = getattr(attr, 'allow_tags', False)
                boolean = getattr(attr, 'boolean', False)
                if boolean:
                    allow_tags = True
                result_repr = display_for_value(value, boolean)
                # Strip HTML tags in the resulting text, except if the
                # function has an "allow_tags" attribute set to True.
                if allow_tags:
                    result_repr = mark_safe(result_repr)
                if isinstance(value, (datetime.date, datetime.time)):
                    row_classes.append("nowrap")
            else:
                if isinstance(f.rel, models.ManyToOneRel):
                    field_val = getattr(result, f.name)
                    if field_val is None:
                        result_repr = EMPTY_CHANGELIST_VALUE
                    else:
                        result_repr = field_val
                else:
                    result_repr = display_for_field(value, f)
                if isinstance(f, (models.DateField, models.TimeField,
                                  models.ForeignKey)):
                    row_classes.append("nowrap")
        if force_text(result_repr) == '':
            result_repr = mark_safe('&nbsp;')

        # If list_display_links not defined, add the link tag to the first
        # field
        if ((first and not cl.list_display_links) or
                field_name in cl.list_display_links):
            table_tag = {True: 'th', False: 'td'}[first]
            first = False
            url = cl.url_for_result(result)
            # Convert the pk to something that can be used in Javascript.
            # Problem cases are long ints (23L) and non-ASCII strings.
            if cl.to_field:
                attr = str(cl.to_field)
            else:
                attr = pk
            value = result.serializable_value(attr)
            result_id = repr(force_text(value))[1:]
            yield format_html('<{0}{1}><a href="{2}"{3}>{4}</a></{5}>',
                              table_tag,
                              mark_safe(len(row_classes) and
                                        ' class="{0}"'.format(
                                            " ".join(row_classes)) or ''),
                              url,
                              format_html(' onclick="opener.dismissRelatedLookupPopup(window, {0}); return false;"', result_id)
                                if cl.is_popup else '',
                              result_repr,
                              table_tag)
        else:
            # By default the fields come from ModelAdmin.list_editable, but if we pull
            # the fields out of the form instead of list_editable custom admins
            # can provide fields on a per request basis
            if (form and field_name in form.fields and not (
                    field_name == cl.model._meta.pk.name and
                    form[cl.model._meta.pk.name].is_hidden)):
                bf = form[field_name]
                result_repr = mark_safe(force_text(bf) + force_text(bf.errors))
            row_class = (len(row_classes) and
                         ' class="{0}"'.format(" ".join(row_classes)) or '')
            yield format_html('<td{0}>{1}</td>', mark_safe(row_class),
                              mark_safe(smart_str(result_repr)))
    if form and not form[cl.model._meta.pk.name].is_hidden:
        yield format_html('<td>{0}</td>',
                          force_text(form[cl.model._meta.pk.name]))


def results(cl):
    """
    Override the ChangeList results template tag to add custom behaviours for
    PBS. This allows us to group by a field (such as category), and add extra
    forms in our list_editable formsets.
    """
    if hasattr(cl.model_admin, 'list_group_by'):
        if hasattr(cl.model_admin, cl.model_admin.list_group_by):
            group_name = getattr(cl.model_admin, cl.model_admin.list_group_by)
        else:
            group_name = None
    else:
        group_name = None

    previous = None
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            group = name_for_group(group_name, cl, res)
            yield ResultList(form, group, previous,
                             items_for_result(cl, res, form))
            previous = group

        # If we have extra forms - append it to our result list to prevent
        # special casing of the template rendering.
        # This would be better in items_for_result, but it's easier for the
        # moment to do it manually here.
        extra_and_empty_forms = cl.formset.extra_forms
        if getattr(cl.model_admin, 'list_empty_form', False):
            extra_and_empty_forms.append(cl.formset.empty_form)
        for form in extra_and_empty_forms:
            group = name_for_group(group_name, cl, None)
            row = []
            for field_name in cl.list_display:
                if field_name in form.fields:
                    bf = form[field_name]
                    result_repr = mark_safe(force_text(form[field_name]))
                    # If the field has errors, alter the <td> class and prepend
                    # a paragraph containing the error messages.
                    if bf.errors:
                        error_list = format_html('<p class="text-error"><i class="icon-warning-sign"></i> {0}</p>', ' '.join(bf.errors))
                        row.append(format_html('<td class="error">{0}{1}</td>', result_repr, error_list))
                    else:
                        row.append(format_html('<td>{0}</td>', result_repr))
                else:
                    row.append(format_html('<td></td>'))
            yield ResultList(form, group, None, row)
    else:
        for res in cl.result_list:
            group = name_for_group(group_name, cl, res)

            yield ResultList(None, group, previous,
                             items_for_result(cl, res, None))
            previous = group


@register.inclusion_tag("admin/change_list_results.html")
def result_list(cl):
    """
    Displays the headers and data list together
    """
    headers = list(result_headers(cl))
    num_sorted_fields = 0
    for h in headers:
        if h['sortable'] and h['sorted']:
            num_sorted_fields += 1

    return {
        'cl': cl,
        'result_hidden_fields': list(result_hidden_fields(cl)),
        'result_headers': headers,
        'num_sorted_fields': num_sorted_fields,
        'results': list(results(cl))}
