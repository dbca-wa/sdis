"""Pythia Admin module."""

from __future__ import unicode_literals

from collections import namedtuple
from functools import update_wrapper, partial
from itertools import chain
import logging
import os
import subprocess

from guardian.admin import GuardedModelAdmin
from reversion.models import Version
from reversion.admin import VersionAdmin

from django.conf import settings
from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.admin.util import flatten_fieldsets, unquote
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.forms.models import modelformset_factory
from django.forms.widgets import Textarea
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.html import escape
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django_select2 import AutoModelSelect2Field, Select2Widget
from django_tablib.admin import TablibAdmin

from pythia.forms import (
    SdisModelForm, BaseInlineEditForm,
    PythiaUserCreationForm, PythiaUserChangeForm)
from pythia.fields import Html2TextField, PythiaArrayField
from pythia.widgets import ArrayFieldWidget, InlineEditWidgetWrapper

logger = logging.getLogger(__name__)
User = get_user_model()
Breadcrumb = namedtuple('Breadcrumb', ['name', 'url'])

# -----------------------------------------------------------------------------#
# swingers.sauth.AuditAdmin, swingers.admin.DetailAdmin


class DetailAdmin(ModelAdmin):
    detail_template = None
    changelist_link_detail = False
    # prevent django-guardian from clobbering change_form template (Scott):
    change_form_template = None

    def get_changelist(self, request, **kwargs):
        """Return custom pythia.views.DetailChangeList."""
        from pythia.views import DetailChangeList
        return DetailChangeList

    def has_change_permission(self, request, obj=None):
        """Return whether user has view permission for object.

        App label and object name are retrieved automatically.
        """
        opts = self.opts
        return request.user.has_perm(
            opts.app_label + '.' + 'change_%s' % opts.object_name.lower())

    def has_view_permission(self, request, obj=None):
        """Return whether user has view permission for object.

        App label and object name are retrieved automatically.
        """
        opts = self.opts
        return request.user.has_perm(
            opts.app_label + '.' + 'view_%s' % opts.object_name.lower())

    def get_urls(self):
        """URL config for pythia."""
        from django.conf.urls import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns(
            '',
            url(r'^$',
                wrap(self.changelist_view),
                name='%s_%s_changelist' % info),
            url(r'^add/$',
                wrap(self.add_view),
                name='%s_%s_add' % info),
            url(r'^(\d+)/history/$',
                wrap(self.history_view),
                name='%s_%s_history' % info),
            url(r'^(\d+)/delete/$',
                wrap(self.delete_view),
                name='%s_%s_delete' % info),
            url(r'^(\d+)/change/$',
                wrap(self.change_view),
                name='%s_%s_change' % info),
            url(r'^(\d+)/$',
                wrap(self.detail_view),
                name='%s_%s_detail' % info),
            )
        return urlpatterns

    def detail_view(self, request, object_id, extra_context=None):
        """Custom detail_view."""
        opts = self.opts

        obj = self.get_object(request, unquote(object_id))

        if not self.has_view_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does '
                            'not exist.') % {
                                'name': force_text(opts.verbose_name),
                                'key': escape(object_id)})

        context = {
            'title': _('Detail %s') % force_text(opts.verbose_name),
            'object_id': object_id,
            'original': obj,
            'is_popup': "_popup" in request.REQUEST,
            'media': self.media,
            'app_label': opts.app_label,
            'opts': opts,
            'has_change_permission': self.has_change_permission(request, obj),
            }
        context.update(extra_context or {})
        return TemplateResponse(request, self.detail_template or [
            "admin/%s/%s/detail.html" % (opts.app_label,
                                         opts.object_name.lower()),
            "admin/%s/detail.html" % opts.app_label,
            "admin/detail.html"
            ], context, current_app=self.admin_site.name)

    def queryset(self, request):
        """Custom queryset."""
        qs = super(DetailAdmin, self).queryset(request)
        return qs.select_related(
            *[field.rsplit('__', 1)[0]
              for field in self.list_display if '__' in field]
            )


class AuditAdmin(VersionAdmin, GuardedModelAdmin, TablibAdmin, ModelAdmin):
    """AuditAdmin for Audit model.

    Mixins: Versions, permissions, spreadsheet export.
    """

    search_fields = ['id', 'creator__username', 'modifier__username',
                     'creator__email', 'modifier__email']
    list_display = ['__unicode__', 'creator', 'modifier', 'created',
                    'modified']
    raw_id_fields = ['creator', 'modifier']
    formats = ['xls', 'json', 'yaml', 'csv', 'html', ]
    change_list_template = None

    def get_list_display(self, request):
        """Custom get_list_display."""
        list_display = list(self.list_display)
        for index, field_name in enumerate(list_display):
            field = getattr(self.model, field_name, None)
            if hasattr(field, "related"):
                list_display.remove(field_name)
                list_display.insert(
                    index, self.display_add_link(request, field.related))
        return list_display

    def display_add_link(self, request, related):
        """Custom display_add_link."""
        def inner(obj):
            opts = related.model._meta
            kwargs = {related.field.name: obj}
            count = related.model._default_manager.filter(**kwargs).count()
            context = {
                'related': related,
                'obj': obj,
                'opts': opts,
                'count': count
                }
            return render_to_string(
                'admin/change_list_links.html',
                RequestContext(request, context)
                )
        inner.allow_tags = True
        inner.short_description = related.opts.verbose_name_plural.title()
        return inner


# end Swingers Admin
# -----------------------------------------------------------------------------#


class UserChoices(AutoModelSelect2Field):
    """Enhance User select list, sorted by last name with a seach filter."""

    queryset = User.objects.order_by('last_name', 'first_name')
    # BUG comes out ordered by username
    search_fields = ['first_name__icontains', 'last_name__icontains',
                     'group_name__icontains', 'affiliation__icontains']

    def __init__(self, *args, **kwargs):
        """Custom init provides Select2Widget."""
        super(UserChoices, self).__init__(*args, **kwargs)
        self.widget = Select2Widget()

    def label_from_instance(self, obj):
        """Custom label is username plus fullname."""
        return "{0} - {1}".format(obj.username, obj.fullname)


class FormfieldOverridesMixin(object):
    """Mixin for InlineWidgetWrapper."""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Provide custom form classes for User."""
        if issubclass(db_field.rel.to, User):
            kwargs.update({'form_class': UserChoices})
        return super(FormfieldOverridesMixin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        """Inject custom edit widgets."""
        formfield = super(FormfieldOverridesMixin,
                          self).formfield_for_dbfield(db_field, **kwargs)

        # skip the RelatedFieldWidgetWrapper
        if ((hasattr(formfield, 'widget') and
             isinstance(formfield.widget,
                        RelatedFieldWidgetWrapper) and
             getattr(self, '_skip_relatedFieldWidget', True))):
            formfield.widget = formfield.widget.widget

        if ((formfield and
             (isinstance(db_field, (Html2TextField, PythiaArrayField)) or
                 isinstance(formfield.widget, Textarea))
             )):
            formfield.widget = InlineEditWidgetWrapper(formfield.widget)

        return formfield


class BaseAdmin(FormfieldOverridesMixin, AuditAdmin):
    """BaseAdmin combines custom forms and AuditAdmin.

    Custom Breadcrumbs start from admin home.
    """

    list_editable_extra = 0
    list_empty_form = False
    object_diff_template = None
    change_form_template = None
    form = BaseInlineEditForm
    formfield_overrides = {PythiaArrayField: {'widget': ArrayFieldWidget}, }

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs.

        Assume that the page being rendered
        knows how to create the last step (current page) of the breadcrumbs.

        Returns a named tuple of ('name', 'url') for each bread crumb.
        """
        # opts = self.model._meta
        return (
            Breadcrumb(_('Home'), reverse('admin:index')), )
        # Breadcrumb(opts.app_label,reverse('admin:app_list',
        #    kwargs={'app_label': opts.app_label},
        #    current_app=self.admin_site.name))

    def get_list_editable(self, request):
        """Return whether list is editable."""
        return self.list_editable

    def revision_view(self, request, object_id, version_id,
                      extra_context=None):
        """Custom revision_view."""
        obj = get_object_or_404(self.model, pk=unquote(object_id))
        version = get_object_or_404(Version, pk=unquote(version_id),
                                    object_id=force_text(obj.pk))
        context = {
            'object': obj,
            'version_date': version.revision.date_created
            }
        context.update(extra_context or {})
        return super(BaseAdmin, self).revision_view(request, object_id,
                                                    version_id,
                                                    extra_context=context)

    def get_changelist_formset(self, request, **kwargs):
        """Return a FormSet class for changelist page if list_editable."""
        defaults = {"formfield_callback": partial(
            self.formfield_for_dbfield, request=request), }

        defaults.update(kwargs)
        fields = self.get_list_editable(request)
        return modelformset_factory(
            self.model, self.get_changelist_form(request, form=SdisModelForm),
            extra=self.list_editable_extra, fields=fields, **defaults)

    # the following wrappers are for better control over admin
    # windows displayed as popups.
    # If the action is a HttpResponseRedirect (rather
    # than a TemplateResponse to e.g. render
    # the same form again but with errors), we can close the popup.
    def add_view(self, request, form_url='', extra_context=None):
        """Add breadcrumbs to our add view."""
        context = {'breadcrumbs': self.get_breadcrumbs(request, add=True)}
        context.update(extra_context or {})
        result = super(BaseAdmin, self).add_view(
            request, form_url=form_url, extra_context=context)

        if ("_popup" in request.REQUEST) and (
                type(result) is HttpResponseRedirect):
            return TemplateResponse(
                request, 'admin/close_popup.html', {},
                current_app=self.admin_site.name)
        return result

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Add breadcrumbs to our change view."""
        obj = get_object_or_404(self.model, pk=unquote(object_id))

        context = {'breadcrumbs': self.get_breadcrumbs(request, obj)}
        context.update(extra_context or {})
        storage = messages.get_messages(request)
        storage.used = True
        result = super(BaseAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=context)

        if ("_popup" in request.REQUEST) and (
                type(result) is HttpResponseRedirect):
            return TemplateResponse(
                request,
                'admin/close_popup.html', {},
                current_app=self.admin_site.name)
        return result

    def changelist_view(self, request, extra_context=None):
        """Add breadcrumbs to our changelist view."""
        context = {'breadcrumbs': self.get_breadcrumbs(request)}
        context.update(extra_context or {})
        return super(BaseAdmin, self).changelist_view(
            request, extra_context=context)

    def delete_view(self, request, object_id, extra_context=None):
        """Add breadcrumbs to our delete view."""
        obj = get_object_or_404(self.model, pk=unquote(object_id))

        context = {
            'breadcrumbs': self.get_breadcrumbs(request, obj),
            'is_popup': "_popup" in request.REQUEST
            }
        context.update(extra_context or {})

        result = super(BaseAdmin, self).delete_view(
            request, object_id, extra_context=context)

        if ("_popup" in request.REQUEST) and (
                type(result) is HttpResponseRedirect):
            return TemplateResponse(
                request, 'admin/close_popup.html', {},
                current_app=self.admin_site.name)
        return result


class UserAdmin(DjangoUserAdmin):
    """Custom UserAdmin."""
    list_display = ('username', 'fullname', 'email', 'program', 'work_center')
    list_per_page = 1000    # sod pagination
    list_filter = ('is_external', 'is_group', 'agreed',
                   'is_staff', 'is_superuser', 'is_active')
    readonly_fields = ('username', 'is_active', 'is_staff', 'is_superuser',
                       'user_permissions', 'last_login', 'date_joined')

    form = PythiaUserChangeForm
    add_form = PythiaUserCreationForm

    fieldsets = (
        ('Name', {
            'description': 'Details required for correct display of name',
            'fields': ('title', 'first_name', 'middle_initials',
                       'last_name', 'group_name', 'affiliation',
                       'is_group', 'is_external'), }),
        ('Contact Details', {
            'description': 'Optional profile information',
            'classes': ('collapse',),
            'fields': ('image', 'email', 'phone', 'phone_alt', 'fax'), }),
        # ('Staff Profile', {
        #    'description':'Staff profile - not used for now',
        #    'classes': ('collapse',),
        #    'fields': ('program', 'work_center', 'profile_text',
        #        'expertise', 'curriculum_vitae', 'projects',
        #        'author_code', 'publications_staff', 'publications_other'),
        # }),
        ('Administrative Details', {
            'description': 'Behind the scenes settings',
            'classes': ('collapse',),
            'fields': ('program', 'work_center', 'username', 'password',
                       'is_active', 'is_staff', 'is_superuser',
                       'date_joined', 'groups'), })
        )

    def program(self, obj):
        """Return the User's program."""
        return obj.pythia_profile.program

    def work_center(self, obj):
        """Return the User's workcenter."""
        return obj.pythia_profile.work_center

    def get_readonly_fields(self, request, obj=None):
        """Determine which fields a User can edit, depending on role and group.

        Superusers can set permissions and details.
        Users can update their own details, but not permissions.
        Users can view other user's profiles read-only.

        Introduces hack property to prevent infinite recursion
         get_fieldsets may call .get_form, which calls .get_readonly_fields
        """
        if request.user.is_superuser:
            # superuser can edit all fields
            return ()
        elif obj and obj.pk:
            return ('is_superuser', 'is_active', 'is_staff', 'date_joined',
                    'groups', 'username')
        else:
            return ('is_superuser', 'is_active', 'is_staff', 'date_joined',
                    'groups')

        # this would work if pythia.models.User would inherit from ActiveModel
        # elif (request.user == obj.creator) and getattr(self, 'hack', True)):
        #    # the user is viewing another profile he created
        #    return super(UserAdmin, self).get_readonly_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        """Custom get_fieldsets."""
        fs = super(UserAdmin, self).get_fieldsets(request, obj)
        return fs

    def get_form(self, request, obj=None, **kwargs):
        """Custom get_form."""
        Form = super(UserAdmin, self).get_form(request, obj, **kwargs)

        class PythiaUserForm(Form):
            # shim to work around broken saving of form as normal user
            # (username should be RO to begin with, no harm done)
            def __init__(self, *args, **kwargs):
                super(PythiaUserForm, self).__init__(*args, **kwargs)
                self.fields['username'].required = False

            def clean_first_name(self):
                first_name = self.cleaned_data['first_name']
                # if not first_name:
                #    raise forms.ValidationError("First name cannot be blank.")
                return first_name

            def clean_last_name(self):
                last_name = self.cleaned_data['last_name']
                # if not last_name:
                #    raise forms.ValidationError("Last name cannot be blank.")
                return last_name

        return PythiaUserForm


class DownloadAdminMixin(ModelAdmin):
    """Mixin providing download as PDF, Latex or simple HTML."""

    download_template = ""
    download_title = ""
    download_subtitle = ""

    def get_urls(self):
        """Add download URLs."""
        from django.conf.urls import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = patterns(
            '',
            url(r'^(\d+)/download/tex/$',
                wrap(self.latex),
                name='%s_%s_download_tex' % info),

            url(r'^(\d+)/download/pdf/$',
                wrap(self.pdf),
                name='%s_%s_download_pdf' % info),

            url(r'^(\d+)/download/html/$',
                wrap(self.simplehtml),
                name='%s_%s_download_html' % info),
            )
        return urlpatterns + super(DownloadAdminMixin, self).get_urls()

    def simplehtml(self, request, object_id):
        """Render as simple HTML."""
        obj = self.get_object(request, unquote(object_id))
        template = self.download_template
        filename = template + ".html"
        now = timezone.localtime(timezone.now())
        # timestamp = now.isoformat().rsplit(".")[0].replace(":", "")[:-2]
        downloadname = filename.replace(' ', '_')
        context = {
            'original': obj,
            'embed': request.GET.get("embed", True),
            'headers': request.GET.get("headers", True),
            'title': obj.download_title,
            'subtitle': obj.download_subtitle,
            'timestamp': now,
            'downloadname': downloadname,
            'baseurl': request.build_absolute_uri("/")[:-1],
            'STATIC_ROOT': settings.STATIC_ROOT,
            'MEDIA_ROOT': settings.MEDIA_ROOT,
            }

        if not request.GET.get("download", False):
            disposition = "inline"
        else:
            disposition = "attachment"

        response = HttpResponse(content_type='text/html')
        response['Content-Disposition'] = '{0}; filename="{1}"'.format(
            disposition, downloadname)

        output = render_to_string(
            "html/" + template + ".html", context,
            context_instance=RequestContext(request))

        response.write(output)
        return response

    def pdf(self, request, object_id):
        """Render as PDF using Latex."""
        obj = self.get_object(request, unquote(object_id))
        template = self.download_template
        texname = template + ".tex"
        filename = template + ".pdf"
        now = timezone.localtime(timezone.now())
        # timestamp = now.isoformat().rsplit(".")[0].replace(":", "")[:-2]
        downloadname = obj.__str__()
        context = {
            'original': obj,
            'embed': request.GET.get("embed", True),
            'headers': request.GET.get("headers", True),
            'title': obj.download_title,
            'subtitle': obj.download_subtitle,
            'timestamp': now,
            'downloadname': downloadname,
            'baseurl': request.build_absolute_uri("/")[:-1],
            'STATIC_ROOT': settings.STATIC_ROOT,
            'MEDIA_ROOT': settings.MEDIA_ROOT,
            }

        if not request.GET.get("download", False):
            disposition = "inline"
        else:
            disposition = "attachment"

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = '{0}; filename="{1}"'.format(
            disposition, downloadname)

        output = render_to_string(
            "latex/" + template + ".tex", context,
            context_instance=RequestContext(request))

        directory = os.path.join(settings.MEDIA_ROOT, "reports", str(obj.id))
        if not os.path.exists(directory):
            os.makedirs(directory)

        if os.path.exists(filename):
            # if outdated then remove all pdfs
            if os.path.exists("outdated"):
                for f in os.listdir(directory):
                    if os.path.splitext(f)[0] == ".pdf":
                        os.remove(os.path.join(directory, f))
            # If cache is valid just return
            else:
                # Until we set outdated file don't cache
                os.remove(os.path.join(directory, filename))
                # with open(filename, "r") as f:
                #    response.write(f.read())
                # return response

        with open(os.path.join(directory, texname), "w") as f:
            f.write(output.encode('utf-8'))

        cmd = ['lualatex', "--interaction", "batchmode", "--output-directory",
               directory, texname]
        try:
            for i in range(2):
                # 2 passes for numbering
                try:
                    subprocess.check_output(cmd)
                except subprocess.CalledProcessError:
                    pass
        except subprocess.CalledProcessError:
            if not os.path.exists(os.path.join(directory, filename)):
                filename = filename.replace(".pdf", ".log")
                response["Content-Type"] = "text"
            else:
                raise

        with open(os.path.join(directory, filename), "r") as f:
            response.write(f.read())

        return response

    def latex(self, request, object_id):
        """Render as Latex source code."""
        obj = self.get_object(request, unquote(object_id))
        template = self.download_template
        filename = template + ".tex"
        now = timezone.localtime(timezone.now())
        # timestamp = now.isoformat().rsplit(".")[0].replace(":", "")[:-2]
        downloadname = filename.replace(' ', '_')
        context = {
            'original': obj,
            'embed': request.GET.get("embed", True),
            'headers': request.GET.get("headers", True),
            'title': obj.download_title,
            'subtitle': obj.download_subtitle,
            'timestamp': now,
            'downloadname': downloadname,
            'baseurl': request.build_absolute_uri("/")[:-1],
            'STATIC_ROOT': settings.STATIC_ROOT,
            'MEDIA_ROOT': settings.MEDIA_ROOT,
            }

        if not request.GET.get("download", False):
            disposition = "inline"
        else:
            disposition = "attachment"

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = '{0}; filename="{1}"'.format(
            disposition, downloadname)

        output = render_to_string(
            "latex/" + template + ".tex", context,
            context_instance=RequestContext(request))
        response.write(output.encode("utf-8"))

        return response


class DivisionAdmin(BaseAdmin, DetailAdmin):
    """Custom DivisionAdmin."""

    exclude = ('effective_to', 'effective_from')
    list_display = ('__str__', 'director_name')

    def director_name(self, obj):
        """Return the director's name."""
        return obj.director.get_full_name()
    director_name.short_description = 'Director'
    director_name.admin_order_field = 'director__last_name'


class ProgramAdmin(BaseAdmin, DetailAdmin):
    """Custom ProgramAdmin."""

    exclude = ('effective_to', 'effective_from')
    list_display = ('__str__', 'cost_center', 'published', 'position',
                    'program_leader_name', 'finance_admin_name',
                    'data_custodian_name')

    def get_readonly_fields(self, request, obj=None):
        """Determine which fields a User can edit, depending on role and group.

        SCD and SMT can update, everyone else is read-only.
        """
        rof = super(ProgramAdmin, self).get_readonly_fields(request, obj)
        scd = Group.objects.get_or_create(name='SCD')[0].user_set.all()
        smt = Group.objects.get_or_create(name='SCD')[0].user_set.all()
        editors = list(set(chain(scd, smt)))
        if not (request.user.is_superuser or request.user in editors):
            rof += ('effective_to', 'effective_from', 'cost_center',
                    'published', 'position', 'program_leader', 'finance_admin',
                    'data_custodian')
        return rof

    def program_leader_name(self, obj):
        return obj.program_leader.__str__()
    program_leader_name.short_description = 'Program Leader'
    program_leader_name.admin_order_field = 'program_leader__last_name'

    def finance_admin_name(self, obj):
        return obj.finance_admin.__str__()
    finance_admin_name.short_description = 'Finance Admin'
    finance_admin_name.admin_order_field = 'finance_admin__last_name'

    def data_custodian_name(self, obj):
        return obj.data_custodian.__str__()
    data_custodian_name.short_description = 'Data Custodian'
    data_custodian_name.admin_order_field = 'data_custodian__last_name'

class WorkCenterAdmin(BaseAdmin, DetailAdmin):
    """Custom WorkCenterAdmin."""

    exclude = ('effective_to', 'effective_from')
    _skip_relatedFieldWidget = False
    list_display = ('__str__', 'district', 'physical_address')


class AreaAdmin(BaseAdmin, DetailAdmin):
    """Custom AreaAdmin."""

    exclude = ('effective_to', 'effective_from')
    list_display = ('__str__', 'area_type')


class RegionAdmin(DetailAdmin):
    """Custom RegionAdmin."""

    list_display = ('__str__', 'northern_extent')


class DistrictAdmin(DetailAdmin):
    """Custom DistrictAdmin."""

    list_display = ('__str__', 'region', 'northern_extent')
