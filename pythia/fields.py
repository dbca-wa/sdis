from __future__ import unicode_literals

#from south.modelsinspector import add_introspection_rules

import json
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import Field
from django.db.models.fields import TextField
from pythia.utils import html2text
from django.utils.safestring import mark_safe

class Html2TextField(TextField):
    def to_python(self, value):
        #return html2text(value)
        return value

#add_introspection_rules([], ["^pythia\.fields\.Html2TextField"])

class PythiaArrayFormField(Field):
    def prepare_value(self, value):
        if value:
            return value
        return '[[""]]'

    def to_python(self, value):
        return value

class PythiaArrayField(TextField):
    def formfield(self, **params):
        param_fix = dict(params)
        param_fix['form_class'] = PythiaArrayFormField
        return super(PythiaArrayField, self).formfield(**param_fix)

    def to_python(self, value):
        return value

#add_introspection_rules([], ["^pythia\.fields\.PythiaArrayField"])

class PythiaTextField(TextField):
    """TODO set allow_tags = True
    """
    def to_python(self, value):
        return mark_safe(value)

    def prepare_value(self, value):
        return value

#add_introspection_rules([], ["^pythia\.fields\.PythiaTextField"])
