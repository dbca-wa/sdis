# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CollaborationProject.academic_list_plain'
        db.add_column(u'projects_collaborationproject', 'academic_list_plain',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CollaborationProject.academic_list_plain'
        db.delete_column(u'projects_collaborationproject', 'academic_list_plain')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'projects.collaborationproject': {
            'Meta': {'ordering': "[u'position', u'-year', u'-number']", 'object_name': 'CollaborationProject', '_ormbases': [u'projects.Project']},
            'academic_list_plain': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'budget': ('pythia.fields.Html2TextField', [], {}),
            'name': ('pythia.fields.Html2TextField', [], {'max_length': '2000'}),
            u'project_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['projects.Project']", 'unique': 'True', 'primary_key': 'True'}),
            'staff_list_plain': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'projects.corefunctionproject': {
            'Meta': {'ordering': "[u'position', u'-year', u'-number']", 'object_name': 'CoreFunctionProject', '_ormbases': [u'projects.Project']},
            u'project_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['projects.Project']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'projects.project': {
            'Meta': {'ordering': "[u'position', u'-year', u'-number']", 'unique_together': "((u'year', u'number'),)", 'object_name': 'Project'},
            'area_list_dpaw_district': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'area_list_dpaw_region': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'area_list_ibra_imcra_region': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'area_list_nrm_region': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'areas': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pythia.Area']", 'symmetrical': 'False', 'blank': 'True'}),
            'comments': ('pythia.fields.Html2TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'projects_project_created'", 'to': u"orm['pythia.User']"}),
            'data_custodian': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'pythia_project_data_custodian'", 'null': 'True', 'to': u"orm['pythia.User']"}),
            'effective_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'effective_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pythia.User']", 'through': u"orm['projects.ProjectMembership']", 'symmetrical': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'modifier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'projects_project_modified'", 'to': u"orm['pythia.User']"}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {'default': '8'}),
            'output_program': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pythia.Division']", 'null': 'True', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_projects.project_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '1000', 'null': 'True', 'blank': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pythia.Program']", 'null': 'True', 'blank': 'True'}),
            'project_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_project_owner'", 'to': u"orm['pythia.User']"}),
            'site_custodian': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'pythia_project_site_custodian'", 'null': 'True', 'to': u"orm['pythia.User']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django_fsm.FSMField', [], {'default': "u'new'", 'max_length': '50'}),
            'tagline': ('pythia.fields.Html2TextField', [], {'null': 'True', 'blank': 'True'}),
            'team_list_plain': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('pythia.fields.Html2TextField', [], {}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'web_resources': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pythia.WebResource']", 'symmetrical': 'False', 'blank': 'True'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2014'})
        },
        u'projects.projectmembership': {
            'Meta': {'ordering': "[u'position']", 'object_name': 'ProjectMembership'},
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '100', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'role': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'time_allocation': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pythia.User']"})
        },
        u'projects.scienceproject': {
            'Meta': {'ordering': "[u'position', u'-year', u'-number']", 'object_name': 'ScienceProject', '_ormbases': [u'projects.Project']},
            u'project_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['projects.Project']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'projects.studentproject': {
            'Meta': {'ordering': "[u'position', u'-year', u'-number']", 'object_name': 'StudentProject', '_ormbases': [u'projects.Project']},
            'level': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'organisation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'project_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['projects.Project']", 'unique': 'True', 'primary_key': 'True'}),
            'student_list_plain': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'pythia.address': {
            'Meta': {'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "u'Australia'", 'max_length': '254'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_address_created'", 'to': u"orm['pythia.User']"}),
            'effective_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'effective_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'extra': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'modifier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_address_modified'", 'to': u"orm['pythia.User']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "u'WA'", 'max_length': '254'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'pythia.area': {
            'Meta': {'ordering': "[u'area_type', u'-northern_extent']", 'object_name': 'Area'},
            'area_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_area_created'", 'to': u"orm['pythia.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'modifier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_area_modified'", 'to': u"orm['pythia.User']"}),
            'mpoly': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '320', 'null': 'True', 'blank': 'True'}),
            'northern_extent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'source_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'pythia.district': {
            'Meta': {'ordering': "[u'-northern_extent']", 'object_name': 'District'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mpoly': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'northern_extent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pythia.Region']"})
        },
        u'pythia.division': {
            'Meta': {'object_name': 'Division'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_division_created'", 'to': u"orm['pythia.User']"}),
            'director': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'leads_divisions'", 'null': 'True', 'to': u"orm['pythia.User']"}),
            'effective_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'effective_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'modifier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_division_modified'", 'to': u"orm['pythia.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '320'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'pythia.program': {
            'Meta': {'ordering': "[u'position', u'cost_center']", 'object_name': 'Program'},
            'cost_center': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_program_created'", 'to': u"orm['pythia.User']"}),
            'data_custodian': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'pythia_data_custodian_on_programs'", 'null': 'True', 'to': u"orm['pythia.User']"}),
            'effective_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'effective_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'finance_admin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'finance_admin_on_programs'", 'null': 'True', 'to': u"orm['pythia.User']"}),
            'focus': ('pythia.fields.Html2TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction': ('pythia.fields.Html2TextField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'modifier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_program_modified'", 'to': u"orm['pythia.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '320'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'program_leader': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'leads_programs'", 'null': 'True', 'to': u"orm['pythia.User']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'pythia.region': {
            'Meta': {'ordering': "[u'-northern_extent']", 'object_name': 'Region'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mpoly': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'northern_extent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'pythia.urlprefix': {
            'Meta': {'object_name': 'URLPrefix'},
            'base_url': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_urlprefix_created'", 'to': u"orm['pythia.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'modifier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_urlprefix_modified'", 'to': u"orm['pythia.User']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "u'Custom Link'", 'max_length': '50'})
        },
        u'pythia.user': {
            'Meta': {'object_name': 'User'},
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'agreed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'author_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'curriculum_vitae': ('pythia.fields.Html2TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'expertise': ('pythia.fields.Html2TextField', [], {'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'group_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_external': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'middle_initials': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'phone_alt': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'profile_text': ('pythia.fields.Html2TextField', [], {'null': 'True', 'blank': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pythia.Program']", 'null': 'True', 'blank': 'True'}),
            'projects': ('pythia.fields.Html2TextField', [], {'null': 'True', 'blank': 'True'}),
            'publications_other': ('pythia.fields.Html2TextField', [], {'null': 'True', 'blank': 'True'}),
            'publications_staff': ('pythia.fields.Html2TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'work_center': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pythia.WorkCenter']", 'null': 'True', 'blank': 'True'})
        },
        u'pythia.webresource': {
            'Meta': {'object_name': 'WebResource'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_webresource_created'", 'to': u"orm['pythia.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'modifier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_webresource_modified'", 'to': u"orm['pythia.User']"}),
            'prefix': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pythia.URLPrefix']"}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        },
        u'pythia.workcenter': {
            'Meta': {'object_name': 'WorkCenter'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_workcenter_created'", 'to': u"orm['pythia.User']"}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pythia.District']", 'null': 'True', 'blank': 'True'}),
            'effective_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'effective_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'modifier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pythia_workcenter_modified'", 'to': u"orm['pythia.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'physical_address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'workcenter_physical_address'", 'to': u"orm['pythia.Address']"}),
            'postal_address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'workcenter_postal_address'", 'to': u"orm['pythia.Address']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['projects']
