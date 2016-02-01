# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
        ('pythia', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='researchfunction',
            name='creator',
            field=models.ForeignKey(related_name='projects_researchfunction_created', editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='researchfunction',
            name='leader',
            field=models.ForeignKey(related_name='pythia_researchfunction_leader', blank=True, to=settings.AUTH_USER_MODEL, help_text='The scientist in charge of the Research Function.', null=True, verbose_name='Function Leader'),
        ),
        migrations.AddField(
            model_name='researchfunction',
            name='modifier',
            field=models.ForeignKey(related_name='projects_researchfunction_modified', editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='researchfunction',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_projects.researchfunction_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='projectmembership',
            name='project',
            field=models.ForeignKey(help_text='The project for the team membership.', to='projects.Project'),
        ),
        migrations.AddField(
            model_name='projectmembership',
            name='user',
            field=models.ForeignKey(help_text='The DPaW staff member to participate in the project team.', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='areas',
            field=models.ManyToManyField(help_text='Areas of relevance', to='pythia.Area', blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='creator',
            field=models.ForeignKey(related_name='projects_project_created', editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='data_custodian',
            field=models.ForeignKey(related_name='pythia_project_data_custodian', blank=True, to=settings.AUTH_USER_MODEL, help_text='The data custodian (SPP E25) responsible for data management, publishing and metadata documentation on the <a target="_" href="http://internal-data.dpaw.wa.gov.au/">data catalogue</a>.', null=True, verbose_name='data custodian'),
        ),
        migrations.AddField(
            model_name='project',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='projects.ProjectMembership'),
        ),
        migrations.AddField(
            model_name='project',
            name='modifier',
            field=models.ForeignKey(related_name='projects_project_modified', editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='output_program',
            field=models.ForeignKey(blank=True, to='pythia.Division', help_text='The DPaW service that this project delivers outputs to.', null=True, verbose_name='Parks and Wildlife Service'),
        ),
        migrations.AddField(
            model_name='project',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_projects.project_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='program',
            field=models.ForeignKey(blank=True, to='pythia.Program', help_text='The Science and Conservation Division Program hosting this project.', null=True, verbose_name='Science and Conservation Division Program'),
        ),
        migrations.AddField(
            model_name='project',
            name='project_owner',
            field=models.ForeignKey(related_name='pythia_project_owner', verbose_name='supervising scientist', to=settings.AUTH_USER_MODEL, help_text='The supervising scientist.'),
        ),
        migrations.AddField(
            model_name='project',
            name='research_function',
            field=models.ForeignKey(blank=True, to='projects.ResearchFunction', help_text='The SCD Research Function this project mainly contributes to.', null=True, verbose_name='Research Function'),
        ),
        migrations.AddField(
            model_name='project',
            name='site_custodian',
            field=models.ForeignKey(related_name='pythia_project_site_custodian', blank=True, to=settings.AUTH_USER_MODEL, help_text='The site custodian responsible for georeferencing and publishing study sites and putting them through corporate approval to mitigate conflicts of study sites and corporate activities.', null=True, verbose_name='site custodian'),
        ),
        migrations.AddField(
            model_name='project',
            name='web_resources',
            field=models.ManyToManyField(help_text='Web resources of relevance: Data, Metadata, Wiki etc.', to='pythia.WebResource', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='project',
            unique_together=set([('year', 'number')]),
        ),
    ]
