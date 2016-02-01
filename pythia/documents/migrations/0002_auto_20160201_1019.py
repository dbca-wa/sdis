# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
        ('pythia', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stafftimeestimate',
            name='creator',
            field=models.ForeignKey(related_name='documents_stafftimeestimate_created', editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stafftimeestimate',
            name='modifier',
            field=models.ForeignKey(related_name='documents_stafftimeestimate_modified', editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='document',
            name='creator',
            field=models.ForeignKey(related_name='documents_document_created', editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='document',
            name='modifier',
            field=models.ForeignKey(related_name='documents_document_modified', editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='document',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_documents.document_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='project',
            field=models.ForeignKey(related_name='documents', to='projects.Project'),
        ),
        migrations.AddField(
            model_name='studentreport',
            name='report',
            field=models.ForeignKey(blank=True, editable=False, to='pythia.ARARReport', help_text='The annual report publishing this StudentReport', null=True),
        ),
        migrations.AddField(
            model_name='stafftimeestimate',
            name='document',
            field=models.ForeignKey(help_text='The Concept Plan.', to='documents.ConceptPlan'),
        ),
        migrations.AddField(
            model_name='progressreport',
            name='report',
            field=models.ForeignKey(blank=True, editable=False, to='pythia.ARARReport', help_text='The annual report publishing this StudentReport', null=True),
        ),
    ]
