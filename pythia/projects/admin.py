"""Project admin."""
from __future__ import absolute_import
from __future__ import unicode_literals
# from django.contrib.auth import get_user_model
from django.contrib.admin.util import unquote
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django_tablib.admin import TablibAdmin
from pythia.admin import BaseAdmin
from pythia.admin import Breadcrumb
from pythia.admin import DetailAdmin
from pythia.admin import DownloadAdminMixin
from pythia.projects.models import PROJECT_CLASS_MAP
# from pythia.templatetags.pythia_base import pythia_urlname
import logging

from functools import update_wrapper
from mail_templated import send_mail
from pythia.widgets import AreasWidgetWrapper
from sdis import settings

logger = logging.getLogger(__name__)


class ResearchFunctionAdmin(BaseAdmin, DetailAdmin):
    """Admin for ResearchFunction."""

    list_display = ('__str__', 'description_safe', 'association_safe',
                    'active', 'function_leader')
    exclude = ('effective_from', 'effective_to', )

    def function_leader(self, obj):
        """Render field function_leader."""
        return obj.leader.get_full_name() if obj.leader else ''
    function_leader.short_description = 'Research Function Leader'
    function_leader.admin_order_field = 'leader__last_name'

    def description_safe(self, obj):
        """Render field description."""
        return mark_safe(obj.description) if obj.description else ''
    description_safe.short_description = 'Description'

    def association_safe(self, obj):
        """Render field association."""
        return mark_safe(obj.association) if obj.association else ''
    association_safe.short_description = 'Association'


class ProjectMembershipAdmin(BaseAdmin, TablibAdmin):
    """Admin for ProjectMembership."""

    list_display = ('__str__', 'project', )
    raw_id_fields = ()
    change_form_template = 'admin/projects/change_form_projectmembership.html'
    formats = ['xls', 'json', 'yaml', 'csv', 'html', ]
    ordering = ["-project__year", "-project__number"]

    def get_readonly_fields(self, request, obj=None):
        """Control write permissions.

        Project is read-only in popup forms, as Membership initialises with the
        Project it belongs to. To change the project of a membership,
        delete the incorrect one, and create the correct membership from
        the correct project.

        User is read-only when changing, but can be set during adding.
        """
        rof = super(ProjectMembershipAdmin, self).get_readonly_fields(request,
                                                                      obj)
        if ('_popup' in request.REQUEST):
            # The user can only be changed when adding (adding someone else),
            # not edit:
            if (request.resolver_match.url_name ==
                    'projects_projectmembership_change'):
                rof += ('user',)

                # if the project is given as request parameter:
                # pre-set project in get_form and make read-only here
                if request.GET.get('project'):
                    rof += ('project',)

        return rof

    # def get_form(self, request, obj=None, **kwargs):
    #    """
    #    Inject additional fields for polymorphic project class
    #    """
    #    result = super(
    #        ProjectMembershipAdmin, self).get_form(request, obj, **kwargs)
    #    result.base_fields['project'].initial = request.GET.get('project')
    #    return result


class ProjectAdmin(BaseAdmin, DetailAdmin, DownloadAdminMixin):
    """Admin for Project."""

    # List view
    list_display = ('project_id', 'type', 'year', 'number', 'project_title',
                    'project_owner_name', 'division', 'program', 'research_function',
                    'status', 'fm_start_date', 'fm_end_date')
    list_display_links = ('project_id', 'project_title')
    list_per_page = 1000    # whoooa
    search_fields = ('title', 'year', 'number')
    list_filter = ('type', 'program', 'status')

    # Detail view
    exclude = ('status', 'effective_from', 'effective_to', 'web_resources')
    download_template = "project_showcase"

    def get_fieldsets(self, request, obj=None):
        """Override get_fieldsets."""
        return (
            ('Project details', {
                'classes': ('collapse in',),
                'description': "Keep mandatory project information up to date",
                'fields': ('year', 'number', 'type', 'title',
                           'project_owner', 'data_custodian',
                           # 'site_custodian',
                           'division', 'program', 'output_program', 'research_function',
                           'start_date', 'end_date'), }),
            ('Project Location', {
                'description': "Enter areas of relevance to the project",
                'classes': ('collapse',),
                'fields': ('areas',), }),
            ('Project display', {
                'description': "Showcase info used in overviews and reports",
                'classes': ('collapse',),
                'fields': ('image', 'tagline', 'comments', 'keywords', 'position'), })
        )

    def division(self, obj):
        """Program Division."""
        return obj.program.division.slug if obj.program and obj.program.division else ''
    division.short_description = 'Division'

    def project_id(self, obj):
        """project_id."""
        return "<a href={0}>{1}</a>".format(
            obj.get_absolute_url(),
            obj.project_year_number)
    project_id.short_description = 'Year-Number'
    project_id.allow_tags = True

    def project_title(self, obj):
        """project_title."""
        return "<a href={0}>{1}</a>".format(
            obj.get_absolute_url(),
            obj.project_title_html)
    project_title.short_description = 'Project name'
    project_title.admin_order_field = 'title'
    project_title.allow_tags = True

    def project_owner_name(self, obj):
        """project_owner_name."""
        return obj.project_owner.get_full_name()
    project_owner_name.short_description = 'Supervising Scientist'
    project_owner_name.admin_order_field = 'project_owner__last_name'

    def fm_start_date(self, obj):
        """start_date."""
        return obj.start_date.strftime('%b %Y') if obj.start_date else '(None)'
    fm_start_date.short_description = 'Start date'
    fm_start_date.admin_order_field = 'start_date'

    def fm_end_date(self, obj):
        """end_date."""
        return obj.end_date.strftime('%b %Y') if obj.end_date else '(None)'
    fm_end_date.short_description = 'End date'
    fm_end_date.admin_order_field = 'end_date'

    def get_changelist(self, request, **kwargs):
        """Get changelist."""
        ChangeList = super(ProjectAdmin,
                           self).get_changelist(request, **kwargs)

        class ProjectChangeList(ChangeList):

            def __init__(self, request, model, list_display,
                         list_display_links, list_filter, date_hierarchy,
                         search_fields, list_select_related, list_per_page,
                         list_max_show_all, list_editable, model_admin):
                # dynamically vary search_fields based on request.GET
                # don't allow empty search_fields because it hides the search
                # box
                search_fields = filter(
                    lambda x: request.GET.get("project_" + x, False),
                    search_fields) or search_fields
                super(ProjectChangeList, self).__init__(
                    request, model, list_display, list_display_links,
                    list_filter, date_hierarchy, search_fields,
                    list_select_related, list_per_page, list_max_show_all,
                    list_editable, model_admin)

            def get_filters(self, request):
                (filter_specs, has_filters, lookup_params,
                 use_distinct) = super(ProjectChangeList, self).get_filters(
                     request)
                has_filters = False

                for search_field in self.search_fields:
                    if "project_" + search_field in lookup_params:
                        del lookup_params[search_field]
                return filter_specs, has_filters, lookup_params, use_distinct

        return ProjectChangeList

    def get_queryset(self, request):
        """Curtomise queryset."""
        return super(ProjectAdmin, self).queryset(request).select_related(
            'program', 'project_owner', 'modifier')

    def response_add(self, request, obj, post_url_continue=None):
        """Customise response."""
        # if post_url_continue is None:
        #    post_url_continue = reverse(
        #        'admin:%s_%s_change' % (self.opts.app_label,
        #                                obj._meta.model_name),
        #        args=(quote(obj.pk),),
        #        current_app=self.admin_site.name)
        return super(ProjectAdmin, self).response_add(request, obj,
                                                      post_url_continue)

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Override the base breadcrumbs: Inject All Projects."""
        ct = ContentType.objects.get_for_model(self.model)
        cl = reverse("admin:{}_{}_changelist".format(ct.app_label, ct.model))
        pcl = reverse('admin:projects_project_changelist')

        if cl == pcl:
            return(
                Breadcrumb(_('Home'), reverse('admin:index')),
                Breadcrumb(_('All Projects'), pcl),)
        else:
            return (Breadcrumb(_('Home'), reverse('admin:index')),
                    Breadcrumb(_('All Projects'), pcl),
                    Breadcrumb(self.model._meta.verbose_name_plural, cl))

    def get_readonly_fields(self, request, obj=None):
        """Control which fields can be updated by whom.

        Only superuser or Group 'SCD' can change project year or number.
        Project type can only be changed in add view, not later on, as this
        would possibly require the deletion and creation of other documents.
        Therefore, setting the project type is an irreversible decision.
        """
        try:
            logger.debug("{0} views {1}".format(request.user.fullname, obj))
        except:
            logger.debug("ProjectAdmin called without object or request.")

        rof = super(ProjectAdmin, self).get_readonly_fields(request, obj)

        if not ((request.user.is_superuser) or
                (request.user in Group.objects.get_or_create(
                name='SCD')[0].user_set.all())):
            # no one except Directorate and su should update year or number
            rof += ('year', 'number',)
            if obj:
                # type only in add view, not in change view
                rof += ('type',)
        return rof

    def get_urls(self):
        """Config for Urls."""
        from django.conf.urls import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name,

        extra_urls = patterns(
            "",
            url(r'^(.+)/transition/$',
                wrap(self.transition_view),
                name='%s_%s_transition' % info),)
        return extra_urls + super(BaseAdmin, self).get_urls()

    def transition_view(self, request, object_id, extra_context=None):
        """Transition view.

        Transition a project through its lifecycle. Raise 403 forbidden if
        it is not possible to perform this action (lack of permission,
        transition not allowed).
        """
        model = self.model
        opts = model._meta
        obj = self.get_object(request, unquote(object_id))
        tx = request.GET.get('transition')

        # Does the thing exist
        if obj is None:
            msg = _('%(name)s object with primary key %(key)r does '
                    'not exist.') % {
                'name': force_text(opts.verbose_name),
                'key': escape(object_id)}
            logger.warning(msg)
            raise Http404(msg)
        else:
            logger.info("{0} wants to {1} for {2} {3}".format(
                request.user,
                tx,
                force_text(opts.verbose_name),
                escape(object_id)
            ))
        # Is current user allowed to do the stuff with the thing
        # Should we use django_fsm.can_proceed instead?
        if tx not in [t.name for t in
                      obj.get_available_user_status_transitions(request.user)]:
            logger.warning("Requested transition '{0}' not available for the "
                           "current user {1}".format(tx, request.user))
            raise PermissionDenied

        t = [t for t in obj.get_available_user_status_transitions(request.user)
             if t.name == tx][0]

        # Who should get notified about this tx?
        recipients = obj.get_users_to_notify(t.target)
        recipients_text = ", ".join([r.fullname for r in recipients])
        explanation = t.custom["explanation"].format(recipients_text)
        # recipients.discard(request.user)

        context = dict(
            instigator=request.user,
            object_name=force_text(obj),
            title=t.custom["verbose"],
            recipients=recipients_text,
            explanation=explanation,
            notify_default=t.custom["notify"],
            breadcrumbs=self.get_breadcrumbs(request, obj),
            model_name=capfirst(force_text(opts.verbose_name_plural)),
            object=obj,
            opts=opts,)
        context.update(extra_context or {})

        # User clicks "confirm" on transition.html
        if request.method == 'POST':

            # run transition, save changed object to db
            getattr(obj, t.name)()
            obj.save()

            # Send email notifications if requested
            do_notify = ('_notify' in request.POST) and (
                request.POST.get('_notify') == u'on')
            tmpl = 'email/email_base.tpl'
            to_emails = [u.email for u in recipients]
            from_email = settings.DEFAULT_FROM_EMAIL
            if do_notify:
                send_mail(tmpl, context, from_email, to_emails)

            # Redirect the user back to the document change page
            redirect_url = reverse('admin:%s_%s_change' %
                                   (opts.app_label, opts.model_name),
                                   args=(object_id,),
                                   current_app=self.admin_site.name)
            return HttpResponseRedirect(redirect_url)

        return TemplateResponse(request, [
            "admin/%s/%s/%s_transition.html" % (
                opts.app_label, opts.model_name, t.name),
            "admin/%s/%s/transition.html" % (opts.app_label, opts.model_name),
            "admin/%s/%s_transition.html" % (opts.app_label, t.name),
            "admin/%s/transition.html" % opts.app_label
        ], context, current_app=self.admin_site.name)

    def history_view(self, request, object_id, extra_context=None):
        """History view."""
        obj = get_object_or_404(self.model, pk=unquote(object_id))

        context = {'breadcrumbs': self.get_breadcrumbs(request, obj)}
        context.update(extra_context or {})
        return super(ProjectAdmin, self).history_view(request, object_id,
                                                      extra_context=context)

    def get_form(self, request, obj=None, **kwargs):
        """Get form override.

        Inject additional fields for polymorphic project class
        """
        temp = self.model
        if (obj):
            self.model = obj.__class__
        result = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
        self.model = temp
        result.base_fields['program'].initial = request.user.program
        result.base_fields['project_owner'].initial = request.user
        result.base_fields['data_custodian'].initial = request.user
        # result.base_fields['site_custodian'].initial = request.user
        return result

    def add_view(self, request, form_url='', extra_context=None):
        """Add view wrapper.

        Wrapper for add_view that forces a surprise class override based on
        project type
        """
        temp = self.model
        if request.method == 'POST':
            form = self.get_form(request)(request.POST, request.FILES)
            if form.is_valid():
                self.model = PROJECT_CLASS_MAP[form.cleaned_data['type']]

        result = super(ProjectAdmin, self).add_view(
            request, form_url, extra_context)
        self.model = temp
        return result

    def formfield_for_dbfield(self, db_field, **kwargs):
        """Inject AreasWidgetWrapper."""
        formfield = super(ProjectAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)
        if db_field.name == "areas":
            formfield.widget = AreasWidgetWrapper(formfield.widget)
        return formfield


class CollaborationProjectAdmin(ProjectAdmin):
    """Admin for External Collaboration."""

    def get_fieldsets(self, request, obj=None):
        """Admin form layout."""
        return (
            ('Partnership details', {
                'classes': ('collapse in',),
                'description': "Details for the overview table in the "
                "Annual Research Activity Report",
                'fields': ('name', 'budget', 'aims', 'description'), }),
        ) + super(CollaborationProjectAdmin, self).get_fieldsets(
            request, obj)


class StudentProjectAdmin(ProjectAdmin):
    """Admin for StudentProject."""

    def get_fieldsets(self, request, obj=None):
        """Admin form layout."""
        return (
            ('Student Project details', {
                'classes': ('collapse in',),
                'description': "Details for the overview table in the "
                "Annual Research Activity Report",
                'fields': ('level', 'organisation',), }),
        ) + super(StudentProjectAdmin, self).get_fieldsets(
            request, obj)
