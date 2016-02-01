# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pythia.fields
import django.contrib.gis.db.models.fields
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('title', models.CharField(help_text='Optional academic title, shown in team lists only if supplied, and only for external team members.', max_length=30, null=True, verbose_name='Academic Title', blank=True)),
                ('first_name', models.CharField(help_text='First name or given name.', max_length=100, null=True, verbose_name='First Name', blank=True)),
                ('middle_initials', models.CharField(help_text='Initials of first and middle names. Will be used in team lists with abbreviated names.', max_length=100, null=True, verbose_name='Initials', blank=True)),
                ('last_name', models.CharField(help_text='Last name or surname.', max_length=100, null=True, verbose_name='Last Name', blank=True)),
                ('is_group', models.BooleanField(default=False, help_text="Whether this profile refers to a group, rather than a natural person. Groups are referred to with their group name, whereas first and last name refer to the group's contact person.", verbose_name='Show as Group')),
                ('group_name', models.CharField(help_text="Group name, if this profile is not a natural person. E.g., 'Goldfields Regional Office'.", max_length=200, null=True, verbose_name='Group name', blank=True)),
                ('affiliation', models.CharField(help_text='Optional affiliation, not required for DPaW. If provided, the affiliation will be appended to the person or group name in parentheses.', max_length=200, null=True, verbose_name='Affiliation', blank=True)),
                ('image', models.ImageField(help_text='If you wish, provide us with a face to the name!', null=True, upload_to='profiles', blank=True)),
                ('email', models.EmailField(max_length=254, null=True, verbose_name='email address', blank=True)),
                ('phone', models.CharField(help_text='The primary phone number during work hours.', max_length=100, null=True, verbose_name='Primary Phone number', blank=True)),
                ('phone_alt', models.CharField(help_text='An alternative phone number during work hours.', max_length=100, null=True, verbose_name='Alternative Phone number', blank=True)),
                ('fax', models.CharField(help_text='The fax number.', max_length=100, null=True, verbose_name='Fax number', blank=True)),
                ('profile_text', pythia.fields.Html2TextField(help_text='A profile text for the staff members, roughly three paragraphs long.', null=True, blank=True)),
                ('expertise', pythia.fields.Html2TextField(help_text='A bullet point list of skills and expertise.', null=True, blank=True)),
                ('curriculum_vitae', pythia.fields.Html2TextField(help_text='A brief curriculum vitae of academic qualifications and professional memberships.', null=True, blank=True)),
                ('projects', pythia.fields.Html2TextField(help_text='Tell us about projects outside SDIS you are involved in.', null=True, verbose_name='Projects outside SDIS', blank=True)),
                ('author_code', models.CharField(help_text='The author code links users to their publications. Staff only.', max_length=255, null=True, verbose_name='Author code', blank=True)),
                ('publications_staff', pythia.fields.Html2TextField(help_text='A list of publications produced for the Department. Staff only.', null=True, verbose_name='Staff publications', blank=True)),
                ('publications_other', pythia.fields.Html2TextField(help_text='A list of publications produced under external affiliation, in press or otherwise unregistered as staff publication.', null=True, verbose_name='Other publications', blank=True)),
                ('is_staff', models.BooleanField(default=True, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('is_external', models.BooleanField(default=False, help_text='Is the user external to DPaW?', verbose_name='External to DPaW')),
                ('agreed', models.BooleanField(default=False, help_text="Has the user agreed to SDIS' Terms and Conditions?", verbose_name='Agreed to the Terms and Conditions', editable=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('effective_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('effective_to', models.DateTimeField(null=True, blank=True)),
                ('street', models.CharField(help_text='The street address', max_length=254)),
                ('extra', models.CharField(help_text='Additional address info', max_length=254, null=True, verbose_name='extra', blank=True)),
                ('city', models.CharField(help_text='The city', max_length=254)),
                ('zipcode', models.CharField(help_text='The zip code', max_length=4)),
                ('state', models.CharField(default='WA', help_text='The state', max_length=254)),
                ('country', models.CharField(default='Australia', help_text='The country', max_length=254)),
                ('creator', models.ForeignKey(related_name='pythia_address_created', editable=False, to=settings.AUTH_USER_MODEL)),
                ('modifier', models.ForeignKey(related_name='pythia_address_modified', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'address',
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='ARARReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('year', models.PositiveIntegerField(help_text='The publication year of this report with four digits, e.g. 2014 for the ARAR 2013-2014', unique=True, verbose_name='Report year', validators=[django.core.validators.MinValueValidator(2013)])),
                ('dm', models.TextField(help_text="The Director's Message in less than 10 000 words.", null=True, verbose_name="Director's Message", blank=True)),
                ('sds_intro', models.TextField(help_text='Introduction paragraph for the Science Delivery Structure section in the ARAR', null=True, verbose_name='Service Delivery Structure', blank=True)),
                ('research_intro', models.TextField(help_text='Introduction paragraph for the Research Activity section in the ARAR', null=True, verbose_name='Research Activities Introduction', blank=True)),
                ('student_intro', models.TextField(help_text='Introduction paragraph for the Student Projects section in the ARAR', null=True, verbose_name='Student Projects Introduction', blank=True)),
                ('pub', models.TextField(help_text='The in less than 100 000 words.', null=True, verbose_name='Publications and Reports', blank=True)),
                ('date_open', models.DateField(help_text='Date from which this ARAR report can be updated.', verbose_name='Open for submissions')),
                ('date_closed', models.DateField(help_text='The cut-off date for any changes.', verbose_name='Closed for submissions')),
                ('creator', models.ForeignKey(related_name='pythia_ararreport_created', editable=False, to=settings.AUTH_USER_MODEL)),
                ('modifier', models.ForeignKey(related_name='pythia_ararreport_modified', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'date_open',
                'verbose_name': 'ARAR',
                'verbose_name_plural': 'ARARs',
            },
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('area_type', models.PositiveSmallIntegerField(default=1, verbose_name='Area Type', choices=[(1, 'Relevant Area Polygon'), (2, 'Fieldwork Area Polygon'), (3, 'DPaW Region'), (4, 'DPaW District'), (5, 'IBRA'), (6, 'IMCRA'), (7, 'Natural Resource Management Region')])),
                ('name', models.CharField(help_text='A human-readable, short but descriptive name.', max_length=320, null=True, blank=True)),
                ('source_id', models.PositiveIntegerField(help_text='The source id', null=True, blank=True)),
                ('northern_extent', models.FloatField(help_text='The maximum northern extent of an Area, useful for sorting by geographic latitude.', null=True, blank=True)),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(help_text='The spatial extent of this feature, stored as WKT.', srid=4326, null=True, verbose_name='Spatial extent', blank=True)),
                ('creator', models.ForeignKey(related_name='pythia_area_created', editable=False, to=settings.AUTH_USER_MODEL)),
                ('modifier', models.ForeignKey(related_name='pythia_area_modified', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['area_type', '-northern_extent'],
                'verbose_name': 'area',
                'verbose_name_plural': 'areas',
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('code', models.CharField(max_length=3, null=True, blank=True)),
                ('northern_extent', models.FloatField(null=True, blank=True)),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(help_text='Optional cache of spatial features.', srid=4326, null=True, blank=True)),
            ],
            options={
                'ordering': ['-northern_extent'],
                'verbose_name': 'district',
                'verbose_name_plural': 'districts',
            },
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('effective_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('effective_to', models.DateTimeField(null=True, blank=True)),
                ('name', models.CharField(max_length=320)),
                ('slug', models.SlugField(help_text='The acronym of the name.')),
                ('creator', models.ForeignKey(related_name='pythia_division_created', editable=False, to=settings.AUTH_USER_MODEL)),
                ('director', models.ForeignKey(related_name='leads_divisions', blank=True, to=settings.AUTH_USER_MODEL, help_text="The Division's Director", null=True)),
                ('modifier', models.ForeignKey(related_name='pythia_division_modified', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['slug', 'name'],
                'verbose_name': 'Departmental Service',
                'verbose_name_plural': 'Departmental Services',
            },
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('effective_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('effective_to', models.DateTimeField(null=True, blank=True)),
                ('name', models.CharField(max_length=320)),
                ('slug', models.SlugField(help_text='A unique slug to be used in folder names etc.')),
                ('published', models.BooleanField(default=True, verbose_name='Publish this Program?')),
                ('position', models.IntegerField(help_text='An arbitrary, ascending ordering number.')),
                ('cost_center', models.CharField(help_text='The three-digit cost center number for the Program.', max_length=3, null=True, blank=True)),
                ('focus', pythia.fields.Html2TextField(help_text="The program's focus as a semicolon-separated list of key words.", null=True, verbose_name='Program focus', blank=True)),
                ('introduction', pythia.fields.Html2TextField(help_text="The program's mission in about 150 to 300 words.", null=True, verbose_name='Program introduction', blank=True)),
                ('creator', models.ForeignKey(related_name='pythia_program_created', editable=False, to=settings.AUTH_USER_MODEL)),
                ('data_custodian', models.ForeignKey(related_name='pythia_data_custodian_on_programs', blank=True, to=settings.AUTH_USER_MODEL, help_text='The default custodian of data sets of this Program.', null=True)),
                ('finance_admin', models.ForeignKey(related_name='finance_admin_on_programs', blank=True, to=settings.AUTH_USER_MODEL, help_text='The finance admin.', null=True)),
                ('modifier', models.ForeignKey(related_name='pythia_program_modified', editable=False, to=settings.AUTH_USER_MODEL)),
                ('program_leader', models.ForeignKey(related_name='leads_programs', blank=True, to=settings.AUTH_USER_MODEL, help_text='The Program Leader', null=True)),
            ],
            options={
                'ordering': ['position', 'cost_center'],
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(help_text='Optional cache of spatial features.', srid=4326, null=True, blank=True)),
                ('name', models.CharField(max_length=64, null=True, blank=True)),
                ('northern_extent', models.FloatField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-northern_extent'],
                'verbose_name': 'region',
                'verbose_name_plural': 'regions',
            },
        ),
        migrations.CreateModel(
            name='URLPrefix',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('effective_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('effective_to', models.DateTimeField(null=True, blank=True)),
                ('slug', models.SlugField(default='Custom Link')),
                ('base_url', models.CharField(help_text='The start of an allowed url (to be joined to an actual url)', max_length=2000)),
                ('creator', models.ForeignKey(related_name='pythia_urlprefix_created', editable=False, to=settings.AUTH_USER_MODEL)),
                ('modifier', models.ForeignKey(related_name='pythia_urlprefix_modified', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'URL prefix',
                'verbose_name_plural': 'URL prefixes',
            },
        ),
        migrations.CreateModel(
            name='WebResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('effective_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('effective_to', models.DateTimeField(null=True, blank=True)),
                ('suffix', models.CharField(max_length=2000)),
                ('creator', models.ForeignKey(related_name='pythia_webresource_created', editable=False, to=settings.AUTH_USER_MODEL)),
                ('modifier', models.ForeignKey(related_name='pythia_webresource_modified', editable=False, to=settings.AUTH_USER_MODEL)),
                ('prefix', models.ForeignKey(editable=False, to='pythia.URLPrefix')),
            ],
            options={
                'verbose_name': 'web resource',
                'verbose_name_plural': 'web resources',
            },
        ),
        migrations.CreateModel(
            name='WebResourceDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('effective_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('effective_to', models.DateTimeField(null=True, blank=True)),
                ('category', models.PositiveSmallIntegerField(default=2, choices=[(1, 'Project related'), (2, 'User related')])),
                ('name', models.CharField(max_length=200)),
                ('url', models.CharField(help_text='The main URL of the web resource', max_length=2000)),
                ('creator', models.ForeignKey(related_name='pythia_webresourcedomain_created', editable=False, to=settings.AUTH_USER_MODEL)),
                ('modifier', models.ForeignKey(related_name='pythia_webresourcedomain_modified', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'web resource domain',
                'verbose_name_plural': 'web resource domains',
            },
        ),
        migrations.CreateModel(
            name='WorkCenter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('slug', models.SlugField()),
                ('creator', models.ForeignKey(related_name='pythia_workcenter_created', editable=False, to=settings.AUTH_USER_MODEL)),
                ('district', models.ForeignKey(blank=True, to='pythia.District', null=True)),
                ('modifier', models.ForeignKey(related_name='pythia_workcenter_modified', editable=False, to=settings.AUTH_USER_MODEL)),
                ('physical_address', models.ForeignKey(related_name='workcenter_physical_address', to='pythia.Address')),
                ('postal_address', models.ForeignKey(related_name='workcenter_postal_address', to='pythia.Address')),
            ],
            options={
                'verbose_name': 'work centre',
                'verbose_name_plural': 'work centres',
            },
        ),
        migrations.AddField(
            model_name='district',
            name='region',
            field=models.ForeignKey(help_text='The region to which this district belongs.', to='pythia.Region'),
        ),
        migrations.AddField(
            model_name='user',
            name='program',
            field=models.ForeignKey(blank=True, to='pythia.Program', help_text='The main Science and Conservation Division Program affilitation.', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
        ),
        migrations.AddField(
            model_name='user',
            name='work_center',
            field=models.ForeignKey(blank=True, to='pythia.WorkCenter', help_text='The work center where most time is spent. Staff only.', null=True),
        ),
    ]
