from __future__ import unicode_literals

from itertools import chain

from django.forms.widgets import SelectMultiple, CheckboxInput
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.contrib.admin.util import quote
from django.forms import widgets
from django import forms

# import json

import copy

# from pythia.utils import text2html, html2text


class ArrayFieldWidget(widgets.TextInput):
    def render(self, name, value, *args, **kwargs):
        html = super(ArrayFieldWidget, self).render(
            name, value, *args, **kwargs)
        tag = ('dataTable%s' % kwargs['attrs'].get('id', ''))

        html += '<div id="{0}"></div><div>&nbsp;</div>'.format(tag)
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        output = '[[""]]'
        try:
            output = data[unicode(name)]
        except:
            pass
        return output



class AreasWidgetWrapper(widgets.Widget):
    def __init__(self, widget):
        self.widget = widget
        self.attrs = widget.attrs

    @property
    def media(self):
        return self.widget.media

    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        obj.widget = copy.deepcopy(self.widget, memo)
        obj.attrs = self.widget.attrs
        memo[id(self)] = obj
        return obj

    def render(self, name, value, *args, **kwargs):
        output = [self.widget.render(name, value, *args, **kwargs)]

        output.append('<script type="text/javascript">')
        output.append('  pythia.areasWidgetWrapper("{0}");'.format(
            kwargs['attrs'].get('id', '')))
        output.append('</script>')

        return mark_safe(''.join(output))

    def build_attrs(self, extra_attrs=None, **kwargs):
        "Helper function for building an attribute dictionary."
        self.attrs = self.widget.build_attrs(extra_attrs=None, **kwargs)
        return self.attrs

    def value_from_datadict(self, data, files, name):
        return self.widget.value_from_datadict(data, files, name)

    def id_for_label(self, id_):
        return self.widget.id_for_label(id_)


class InlineEditWidgetWrapper(widgets.Widget):
    # adapted from django.contrib.admin.widgets.RelatedFieldWidgetWrapper
    # TODO: this will need to be a little bit refactored in order to support
    # widgets other than TinyMCE
    # I suppose we could have a map of widgets to wrappers (wrapping js)?
    # we'll probably want to use different code for SelectWidgets, TextWidgets,
    # TextInputs, etc.
    # this should be fairly robust in order to work across all the widgets

    # make this a tuple so that we can go from more specific to more general
    # having Widget last to catch anything without fit


    # Changes 2014: We reverted to store HTML, not Markdown in
    # pythia.fields.Html2TextField
    # Enable lines with "MARKDOWN" comments to convert HTML edited in the
    # widget to Markdown in the db field.
    widget_overrides = (
        (ArrayFieldWidget, 'pythia.handsontable("%s", "%s");'),
        (widgets.TextInput, 'pythia.inlineEditTextInput("%s", "%s");'),
        (widgets.Textarea, 'pythia.inlineEditTextarea("%s", "%s");'),
        (widgets.Select, 'pythia.inlineEditSelect("%s", "%s");'),
        (widgets.Widget, 'pythia.inlineEditWidget("%s", "%s");'),
    )

    def __init__(self, widget):
        self.widget = widget
        self.attrs = widget.attrs

    @property
    def media(self):
        if isinstance(self.widget, widgets.Textarea):
            cdn = 'https://static.dpaw.wa.gov.au/static/libs/'
            return forms.Media(
                js=[cdn + 'tinymce/4.3.12/tinymce.min.js',
                    cdn + 'tinymce/4.3.12/jquery.tinymce.min.js'
            ]) + self.widget.media
        else:
            return self.widget.media

    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        obj.widget = copy.deepcopy(self.widget, memo)
        obj.attrs = self.widget.attrs
        memo[id(self)] = obj
        return obj

    def render(self, name, value, *args, **kwargs):
        if not hasattr(self, 'form'):
            # the form has not been injected to the widget, failover to the
            # original widget
            return mark_safe(self.widget.render(name, value, *args, **kwargs))

        opts = self.form.instance._meta
        # url refers to the POST location used by TinyMCE's AJAX save function.
        # If we're on an add page, we don't want to POST save anything.
        url = None
        if self.form.instance.pk:
            url = reverse('admin:%s_%s_change' % (opts.app_label,
                                                  opts.model_name),
                          args=(quote(self.form.instance.pk),))

        output = [self.widget.render(name, value, *args, **kwargs)]
        # name - input name, value, kwargs['attrs']['id'] input id
        for klass, js in self.widget_overrides:
            if isinstance(self.widget, klass):
                output.append('<script type="text/javascript">')
                output.append(js % (kwargs['attrs'].get('id', ''), url))
                output.append('</script>')
                break

        return mark_safe(''.join(output))

    def build_attrs(self, extra_attrs=None, **kwargs):
        "Helper function for building an attribute dictionary."
        self.attrs = self.widget.build_attrs(extra_attrs=None, **kwargs)
        return self.attrs

    def value_from_datadict(self, data, files, name):
        value = self.widget.value_from_datadict(data, files, name)

        # MARKDOWN: enable next two lines to store markdown
        # if value and isinstance(self.widget, widgets.Textarea):
        #    value = html2text(value)

        return value

    def id_for_label(self, id_):
        return self.widget.id_for_label(id_)


class NumberInput(widgets.TextInput):
    input_type = 'number'


class LocationWidget(widgets.MultiWidget):

    DIRECTION_CHOICES = (
        ('', '---'),
        ('N', 'N'),
        ('NNE', 'NNE'),
        ('NE', 'NE'),
        ('ENE', 'ENE'),
        ('E', 'E'),
        ('ESE', 'ESE'),
        ('SE', 'SE'),
        ('SSE', 'SSE'),
        ('S', 'S'),
        ('SSW', 'SSW'),
        ('SW', 'SW'),
        ('WSW', 'WSW'),
        ('W', 'W'),
        ('WNW', 'WNW'),
        ('NW', 'NW'),
        ('NNW', 'NNW'),
    )

    def __init__(self, attrs=None):
        _widgets = (
            widgets.TextInput(attrs={'class': 'locn_locality'}),
            NumberInput(attrs={'class': 'locn_distance', 'maxlength': '4'}),
            widgets.Select(attrs={'class': 'locn_direction'},
                           choices=LocationWidget.DIRECTION_CHOICES),
            widgets.TextInput(attrs={'class': 'locn_town'}),
        )
        super(LocationWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            value = value.split('|')
            if len(value) > 1:
                return [value[0] or None, value[1] or None,
                        value[2] or None, value[3] or None]
            else:
                try:
                    value[0].split("Within the locality of ")[1]
                    return [value[0].split("Within the locality of ")[1],
                            None, None, None]
                except IndexError:
                    # Can't parse the string correctly, fall back to just using
                    # the value.
                    return [value[0], None, None, None]
        return [None, None, None, None]

    def format_output(self, rendered_widgets):
        return rendered_widgets[0] + ' - ' + rendered_widgets[1] + 'km(s) ' +\
        rendered_widgets[2] + ' of ' + rendered_widgets[3]

# TODO: this code should work for Django 1.6
#
#class CheckboxFieldRenderer(widgets.CheckboxFieldRenderer):
#    def render(self):
#        output = []
#        for widget in self:
#            output.append(format_html(force_text(widget)))
#        return mark_safe('\n'.join(output))
#
#
#class CheckboxSelectMultiple(widgets.CheckboxSelectMultiple):
#    renderer = CheckboxFieldRenderer


# This code is from Django 1.5
class CheckboxSelectMultiple(SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = []
        # Normalize to strings
        str_values = set([force_text(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = format_html(' for="{0}"', final_attrs['id'])
            else:
                label_for = ''

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_text(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = force_text(option_label)
            output.append(format_html('<label{0} class="checkbox">{1} {2}</label>',
                                      label_for, rendered_cb, option_label))
        return mark_safe('\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_
