# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pythia.fields
import pythia.documents.models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        #('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', django_fsm.FSMField(default='new', max_length=50, verbose_name='Document Status', choices=[('new', 'New document'), ('inreview', 'Review requested'), ('inapproval', 'Approval requested'), ('approved', 'Approved')])),
                ('pdf', models.FileField(help_text='The latest, greatest and PDFest version of all times', upload_to=pythia.documents.models.documents_upload_to, null=True, editable=False, blank=True)),
            ],
            options={
                'display_order': 0,
                'get_latest_by': 'created',
                'verbose_name': 'Document',
                'verbose_name_plural': 'Documents',
            },
        ),
        migrations.CreateModel(
            name='StaffTimeEstimate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.TextField(blank=True, help_text='The role of the involved staff.', null=True, verbose_name='Role', choices=[(1, 'Supervising Scientist'), (2, 'Research Scientist'), (3, 'Technical Officer'), (9, 'External Collaborator'), (10, 'Other (specify)')])),
                ('staff', models.TextField(help_text='The involved staff if known.', null=True, verbose_name='Staff', blank=True)),
                ('year1', models.TextField(help_text='The time allocation in year 1 of the project in FTE.', null=True, verbose_name='Year 1', blank=True)),
                ('year2', models.TextField(help_text='The time allocation in year 2 of the project in FTE.', null=True, verbose_name='Year 2', blank=True)),
                ('year3', models.TextField(help_text='The time allocation in year 3 of the project in FTE.', null=True, verbose_name='Year 3', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ConceptPlan',
            fields=[
                ('document_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='documents.Document')),
                ('summary', models.TextField(help_text='Summarise the project in up to 500 words.', null=True, verbose_name='Background and Aims', blank=True)),
                ('outcome', models.TextField(help_text='Summarise the expected outcome in up to 500 words.', null=True, verbose_name='Expected outcome', blank=True)),
                ('collaborations', models.TextField(help_text='List expected collaborations in up to 500 words.', null=True, verbose_name='Expected collaborations', blank=True)),
                ('strategic', models.TextField(help_text='Describe the strategic context and management implications in up to 500 words.', null=True, verbose_name='Strategic context', blank=True)),
                ('staff', pythia.fields.PythiaArrayField(default=b'[["Role", "Year 1", "Year 2", "Year 3"], ["Scientist", "", "", ""], ["Technical", "", "", ""], ["Volunteer", "", "", ""], ["Collaborator", "", "", ""]]', help_text="Summarise the staff time allocation by role for the first three years, or for a time span appropriate for the Project's life time.", null=True, verbose_name='Staff time allocation', blank=True)),
                ('budget', pythia.fields.PythiaArrayField(default=b'[["Source", "Year 1", "Year 2", "Year 3"], ["Consolidated Funds (DPaW)", "", "", ""], ["External Funding", "", "", ""]]', help_text="Indicate the operating budget for the first three years, or for a time span appropriate for the Project's life time.", null=True, verbose_name='Indicative operating budget', blank=True)),
                ('director_scd_comment', models.TextField(help_text='Optional comment to clarify endorsement or provide feedback', verbose_name="Science and Conservation Division Director's Comment", null=True, editable=False, blank=True)),
                ('director_outputprogram_comment', models.TextField(help_text='Optional comment to clarify endorsement or provide feedback', verbose_name="Comment of the Output Program's Director", null=True, editable=False, blank=True)),
            ],
            options={
                'display_order': 10,
                'verbose_name': 'Concept Plan',
                'verbose_name_plural': 'Concept Plans',
            },
            bases=('documents.document',),
        ),
        migrations.CreateModel(
            name='ProgressReport',
            fields=[
                ('document_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='documents.Document')),
                ('is_final_report', models.BooleanField(default=False, help_text='Whether this report is the final progress report after submitting a project closure request.', verbose_name='Is final report', editable=False)),
                ('year', models.PositiveIntegerField(default=pythia.documents.models.get_current_year, help_text='The year on which this progress report reports on with four digits, e.g. 2014 for FY 2013/14.', verbose_name='Report year', editable=False)),
                ('context', models.TextField(help_text='A shortened introduction / background for the annual activity update. Aim for 100 to 150 words.', null=True, verbose_name='Context', blank=True)),
                ('aims', models.TextField(help_text='A bullet point list of aims for the annual activity update. Aim for 100 to 150 words. One bullet point per aim.', null=True, verbose_name='Aims', blank=True)),
                ('progress', models.TextField(help_text='Current progress and achievements for the annual activity update. Aim for 100 to 150 words. One bullet point per achievement.', null=True, verbose_name='Progress', blank=True)),
                ('implications', models.TextField(help_text='Management implications for the annual activity update. Aim for 100 to 150 words. One bullet point per implication.', null=True, verbose_name='Management implications', blank=True)),
                ('future', models.TextField(help_text='Future directions for the annual activity update. Aim for 100 to 150 words. One bullet point per direction.', null=True, verbose_name='Future directions', blank=True)),
            ],
            options={
                'display_order': 30,
                'verbose_name': 'Progress Report',
                'verbose_name_plural': 'Progress Reports',
            },
            bases=('documents.document',),
        ),
        migrations.CreateModel(
            name='ProjectClosure',
            fields=[
                ('document_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='documents.Document')),
                ('scientific_outputs', models.TextField(help_text='List key publications and documents.', null=True, verbose_name='Key publications and documents', blank=True)),
                ('knowledge_transfer', models.TextField(help_text='List knowledge transfer achievements.', null=True, verbose_name='Knowledge Transfer', blank=True)),
                ('data_location', models.TextField(help_text='Paste links to all datasets of this project on the <a target="_" href="http://internal-data.dpaw.wa.gov.au/">data catalogue</a>.', null=True, verbose_name='Dataset links', blank=True)),
                ('hardcopy_location', models.TextField(help_text='Location of hardcopy of all project data.', null=True, verbose_name='Hardcopy location', blank=True)),
                ('backup_location', models.TextField(help_text='Location of electronic project data.', verbose_name='Backup location', null=True, editable=False, blank=True)),
            ],
            options={
                'display_order': 50,
                'verbose_name': 'Project Closure',
                'verbose_name_plural': 'Project Closures',
            },
            bases=('documents.document',),
        ),
        migrations.CreateModel(
            name='ProjectPlan',
            fields=[
                ('document_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='documents.Document')),
                ('related_projects', models.TextField(help_text='Name related SPPs and the extent you have consulted with their project leaders (SPP A6).', verbose_name='Related Science Projects', null=True, editable=False, blank=True)),
                ('background', models.TextField(help_text='Describe project background (SPP C16) including a literature review.', null=True, verbose_name='Background', blank=True)),
                ('aims', models.TextField(help_text='List project aims (SPP C17).', null=True, verbose_name='Aims', blank=True)),
                ('outcome', models.TextField(help_text='Describe expected project outcome.', null=True, verbose_name='Expected outcome', blank=True)),
                ('knowledge_transfer', models.TextField(help_text='Anticipated users of the knowledge to be gained, and technology transfer strategy (SPP C19).', null=True, verbose_name='Knowledge transfer', blank=True)),
                ('project_tasks', models.TextField(help_text='Major tasks, milestones and outputs (SPP C20). Indicate delivery time frame for each task.', null=True, verbose_name='Tasks and Milestones', blank=True)),
                ('references', models.TextField(help_text='Paste in the bibliography of your literature research (SPP C21).', null=True, verbose_name='References', blank=True)),
                ('methodology', models.TextField(help_text='Describe the study design and statistical analysis (SPP D22).', null=True, verbose_name='Methodology', blank=True)),
                ('bm_endorsement', models.CharField(default='required', choices=[('required', 'required'), ('denied', 'denied'), ('granted', 'granted')], max_length=100, blank=True, help_text="The Biometrician's endorsement of the methodology's statistical validity.", null=True, verbose_name="Biometrician's Endorsement")),
                ('involves_plants', models.BooleanField(default=False, help_text='Tick to indicate that this project will collect plant specimens, which will require endorsement by the Herbarium Curator.', verbose_name='Involves plant specimen collection')),
                ('no_specimens', models.TextField(help_text="Estimate the number of collected vouchered specimens (SPP E23). Provide any additional info required for the Harbarium Curator's endorsement.", null=True, verbose_name='No. specimens', blank=True)),
                ('hc_endorsement', models.CharField(default='not required', choices=[('not required', 'not required'), ('required', 'required'), ('denied', 'denied'), ('granted', 'granted')], max_length=100, blank=True, help_text="The Herbarium Curator's endorsement of the planned collection of voucher specimens.", null=True, verbose_name="Herbarium Curator's Endorsement")),
                ('involves_animals', models.BooleanField(default=False, help_text='Tick to indicate that this project will involve direct interaction with animals, which will require endorsement by the Animal Ethics Committee.', verbose_name='Involves interaction with vertebrate animals (excl. fish)')),
                ('ae_endorsement', models.CharField(default='not required', choices=[('not required', 'not required'), ('required', 'required'), ('denied', 'denied'), ('granted', 'granted')], max_length=100, blank=True, help_text="The Animal Ethics Committee's endorsement of the planned direct interaction with animals. Approval process is currently handled outside of SDIS.", null=True, verbose_name="Animal Ethics Committee's Endorsement")),
                ('data_management', models.TextField(help_text='Describe how and where data will be maintained, archived, cataloged (SPP E24). Read DPaW guideline 16.', null=True, verbose_name='Data management', blank=True)),
                ('data_manager_endorsement', models.CharField(editable=False, choices=[('not required', 'not required'), ('required', 'required'), ('denied', 'denied'), ('granted', 'granted')], max_length=100, blank=True, help_text="The Data Manager's endorsement of the project's data management. The DM will help to set up Wiki pages, data catalog permissions, scientific sites, and advise on metadata creation.", null=True, verbose_name="Data Manager's Endorsement")),
                ('operating_budget', pythia.fields.PythiaArrayField(default=b'[["Source", "Year 1", "Year 2", "Year 3"], ["FTE Scientist", "", "", ""], ["FTE Technical", "", "", ""], ["Equipment", "", "", ""], ["Vehicle", "", "", ""], ["Travel", "", "", ""], ["Other", "", "", ""], ["Total", "", "", ""]]', help_text='Estimated budget: consolidated DPaW funds', null=True, verbose_name='Consolidated Funds', blank=True)),
                ('operating_budget_external', pythia.fields.PythiaArrayField(default=b'[["Source", "Year 1", "Year 2", "Year 3"], ["Salaries, Wages, Overtime", "", "", ""], ["Overheads", "", "", ""], ["Equipment", "", "", ""], ["Vehicle", "", "", ""], ["Travel", "", "", ""], ["Other", "", "", ""], ["Total", "", "", ""]]', help_text='Estimated budget: external funds', null=True, verbose_name='External Funds', blank=True)),
            ],
            options={
                'display_order': 20,
                'verbose_name': 'Project Plan',
                'verbose_name_plural': 'Project Plans',
            },
            bases=('documents.document',),
        ),
        migrations.CreateModel(
            name='StudentReport',
            fields=[
                ('document_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='documents.Document')),
                ('year', models.PositiveIntegerField(default=pythia.documents.models.get_current_year, help_text='The year on which this progress report reports on with four digits, e.g. 2014', verbose_name='Report year', editable=False)),
                ('progress_report', models.TextField(help_text='Report the Progress in max. 150 words.', null=True, verbose_name='Progress Report', blank=True)),
            ],
            options={
                'display_order': 40,
                'verbose_name': 'Student Report',
                'verbose_name_plural': 'Student Reports',
            },
            bases=('documents.document',),
        ),
        migrations.AddField(
            model_name='document',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_documents.document_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
