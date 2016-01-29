# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
        ('pythia', '0001_initial'),
        ('projects', '0001_initial'),
    ]

    operations = [
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
