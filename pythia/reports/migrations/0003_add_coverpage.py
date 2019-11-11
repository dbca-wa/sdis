# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ARARReport.coverpage'
        db.add_column(u'pythia_ararreport', 'coverpage',
                      self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ARARReport.pdf'
        db.delete_column(u'pythia_ararreport', 'coverpage')

    models = {}

    complete_apps = ['reports']
