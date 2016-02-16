from __future__ import unicode_literals, absolute_import

from datetime import date
from django.contrib.auth.models import Group
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, Http404

from pythia.admin import BaseAdmin, Breadcrumb, DownloadAdminMixin
from pythia.models import User
from pythia.projects.models import PROJECT_CLASS_MAP
from pythia.templatetags.pythia_base import pythia_urlname
from pythia.widgets import AreasWidgetWrapper
from pythia.utils import mail_from_template

from functools import update_wrapper
from sdis import settings



class ResearchFunctionAdmin(BaseAdmin, DownloadAdminMixin):

    list_display = ('__str__','association')
    exclude = ('effective_from', 'effective_to', 'leader')

    def function_leader(self, obj):
        return obj.leader.get_full_name()
    function_leader.short_description = 'Research Function Leader'
    function_leader.admin_order_field = 'leader__last_name'

    def get_breadcrumbs(self, request, obj=None, add=False):
        """
        Override the base breadcrumbs to add the research function list to the trail.
        """
        return (
            Breadcrumb(_('Home'), reverse('admin:index')),
            Breadcrumb(_('Research Functions'),
                       reverse('admin:projects_researchfunction_changelist'))
        )


class ProjectMembershipAdmin(BaseAdmin):
    list_display = ('project', 'user', 'role')
    raw_id_fields = ()
    change_form_template = 'admin/projects/change_form_projectmembership.html'

    def get_readonly_fields(self, request, obj=None):
        """Project is read-only in popup forms, as Membership initialises with the
        Project it belongs to. To change the project of a membership,
        delete the incorrect one, and create the correct membership from
        the correct project.

        User is read-only when changing, but can be set during adding.
        This enables


        """
        rof = super(ProjectMembershipAdmin, self).get_readonly_fields(request,
                                                                      obj)
        if ('_popup' in request.REQUEST):
            # The user can only be changed when adding (adding someone else), not edit:
            if request.resolver_match.url_name == 'projects_projectmembership_change':
                rof += ('user',)

                # if the project is given as request parameter:
                # pre-set project in get_form and make read-only here
                if request.GET.get('project'):
                    rof += ('project',)


        return rof

    #def get_form(self, request, obj=None, **kwargs):
    #    """
    #    Inject additional fields for polymorphic project class
    #    """
    #    result = super(ProjectMembershipAdmin, self).get_form(request, obj, **kwargs)
    #    result.base_fields['project'].initial = request.GET.get('project')
    #    return result



class ProjectAdmin(BaseAdmin):
    list_display = ('project_id', 'project_title', 'type', 'year', 'number',
                    'project_owner_name', 'program', 'research_function',
                    'status', 'fm_start_date', 'fm_end_date')
    list_per_page = 1000    # whoooa
    exclude = ('status', 'effective_from', 'effective_to', 'web_resources')
    list_display_links = ('project_id', 'project_title')
    search_fields = ('title', 'year', 'number')
    list_filter = ('type', 'program', 'status')

    def get_fieldsets(self, request, obj=None):
        #print("project admin get fieldsets")
        #fs = super(ProjectAdmin, self).get_fieldsets(request, obj)
        #return fs
        return (
        ('Project details', {
            'classes': ('collapse in',),
            'description': "Keep mandatory project information up to date",
            'fields': ('year','number','type', 'title',
                'project_owner',
                #'site_custodian',
                'data_custodian',
                'program','output_program','research_function',
                'start_date', 'end_date'),}),
        ('Project Location', {
            'description': "Enter areas of relevance to the project",
            'classes': ('collapse',),
            'fields': ('areas',),}),
        ('Project display', {
            'description': "Determine how and where this project is displayed",
            'classes': ('collapse',),
            'fields': ('image', 'tagline', 'comments', 'position'),})
        )



    def project_id(self, obj):
        return obj.project_year_number
    project_id.short_description = 'ID'

    def project_title(self, obj):
        return obj.project_title_html
    project_title.short_description = 'Project name'
    project_title.admin_order_field = 'title'
    project_title.allow_tags = True

    def project_owner_name(self, obj):
        return obj.project_owner.get_full_name()
    project_owner_name.short_description = 'Supervising Scientist'
    project_owner_name.admin_order_field = 'project_owner__last_name'

    def fm_start_date(self, obj):
        return obj.start_date.strftime('%b %Y') if obj.start_date else '(None)'
    fm_start_date.short_description = 'Start date'
    fm_start_date.admin_order_field = 'start_date'

    def fm_end_date(self, obj):
        return obj.end_date.strftime('%b %Y') if obj.end_date else '(None)'
    fm_end_date.short_description = 'End date'
    fm_end_date.admin_order_field = 'end_date'

    def get_changelist(self, request, **kwargs):
        ChangeList = super(ProjectAdmin, self).get_changelist(request,
                                                              **kwargs)

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
                    list_editable, model_admin
                )

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

    #def get_queryset(self, request):
    #    return super(ProjectAdmin, self).queryset(request).select_related(
    #        'program', 'project_owner', 'modifier')

    def response_add(self, request, obj, post_url_continue=None):
        #if post_url_continue is None:
        #    post_url_continue = reverse(
        #        'admin:%s_%s_change' % (self.opts.app_label,
        #                                obj._meta.model_name),
        #        args=(quote(obj.pk),),
        #        current_app=self.admin_site.name)
        return super(ProjectAdmin, self).response_add(request, obj,
                                                      post_url_continue)

    def get_breadcrumbs(self, request, obj=None, add=False):
        """
        Override the base breadcrumbs to add the project list to the trail.
        """
        return (
            Breadcrumb(_('Home'), reverse('admin:index')),
            Breadcrumb(_('All projects'),
                       reverse('admin:projects_project_changelist'))
        )

    def get_readonly_fields(self, request, obj=None):
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
        from django.conf.urls import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name,

        extra_urls = patterns(
            "",
            url(r'^(.+)/transition/$', wrap(self.transition_view),
                name='%s_%s_transition' % info),
        )
        return extra_urls + super(BaseAdmin, self).get_urls()

    def transition_view(self, request, object_id, extra_context=None):
        """
        Transition a project through its lifecycle. Raise 403 forbidden if
        it is not possible to perform this action (lack of permission,
        transition not allowed).
        """
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does '
                            'not exist.') % {
                                'name': force_text(opts.verbose_name),
                                'key': escape(object_id)})

        # Check if the transition is possible
        try:
            transition = request.GET.get('transition')
            func = dict(obj.get_available_status_transitions())[transition]
        except KeyError:
            raise Http404(_('Missing transition key for object %(name)s '
                            'with primary key %(key)r.') % {
                                'name': force_text(opts.verbose_name),
                                'key': escape(object_id)})

        if not request.user.has_perm(func.permission, obj):
            raise PermissionDenied

        if request.method == 'POST':
            # Do the transition. django-fsm is broken here, not sure
            # what is going on, but it's not setting bound_func.im_func
            # Hack around it for the time being.
            meta = func._django_fsm
            if not (meta.has_transition(obj) and meta.conditions_met(obj)):
                raise Http404

            getattr(obj, func.__name__)()

            if ('_notify' in request.POST) and (
                    request.POST.get('_notify') == u'on'):
                # fire off a notification email
                recipients = obj.get_users_to_notify(transition)
                recipients.discard(request.user)
                # FIXME: short circuit
                recipients = [User.objects.get(username='florianm')]
                context = {
                    'instigator': request.user,
                    'object_name': 'project {0} ({1})'.format(
                        obj.project_type_year_number, obj.title_plain),
                    'object_url': request.build_absolute_uri(
                        reverse(pythia_urlname(obj.opts, 'change'), args=[obj.pk])),
                    'status': [x[1] for x in obj.STATUS_CHOICES if
                        x[0] == transition][0],
                    'explanation': True,
                }
                mail_from_template('{0} has been updated'.format(
                    obj.project_type_year_number),
                    list(recipients), 'email/email_base', context)

            # Redirect the user back to the project change page
            redirect_url = reverse('admin:%s_%s_change' %
                                   (opts.app_label, opts.model_name),
                                   args=(object_id,),
                                   current_app=self.admin_site.name)
            return HttpResponseRedirect(redirect_url)

        context = dict(
            title=_('%s: %s') % (func.verbose_name, force_text(obj)),
            breadcrumbs=self.get_breadcrumbs(request, obj),
            transition_name=func.verbose_name,
            model_name=capfirst(force_text(opts.verbose_name_plural)),
            object=obj,
            opts=opts,
        )
        context.update(extra_context or {})

        return TemplateResponse(request, [
            "admin/%s/%s/%s_transition.html" % (
                opts.app_label, opts.model_name, transition),
            "admin/%s/%s/transition.html" % (opts.app_label, opts.model_name),
            "admin/%s/%s_transition.html" % (opts.app_label, transition),
            "admin/%s/transition.html" % opts.app_label
        ], context, current_app=self.admin_site.name)

    def history_view(self, request, object_id, extra_context=None):
        obj = get_object_or_404(self.model, pk=unquote(object_id))

        context = {
            'breadcrumbs': self.get_breadcrumbs(request, obj)
        }
        context.update(extra_context or {})
        return super(ProjectAdmin, self).history_view(request, object_id,
                                                       extra_context=context)

    def get_form(self, request, obj=None, **kwargs):
        """
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
        #result.base_fields['site_custodian'].initial = request.user
        return result

    def add_view(self, request, form_url='', extra_context=None):
        """
        Wrapper for add_view that forces a surprise class override based on
        project type
        """
        temp = self.model
        if request.method == 'POST':
            form = self.get_form(request)(request.POST, request.FILES)
            if form.is_valid():
                self.model = PROJECT_CLASS_MAP[form.cleaned_data['type']]

        result = super(ProjectAdmin, self).add_view(request, form_url,
                extra_context)
        self.model = temp
        return result

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(ProjectAdmin, self).formfield_for_dbfield(db_field,
                                                                    **kwargs)
        if db_field.name == "areas":
            formfield.widget = AreasWidgetWrapper(formfield.widget)
        return formfield

class CollaborationProjectAdmin(ProjectAdmin):

    def get_fieldsets(self, request, obj=None):
        #print("COL admin get fieldsets")
        return  (
        ('Collaboration details', {
            'classes': ('collapse in',),
            'description': "Details for the overview table in the "
            "Annual Research Activity Report",
            'fields': ('name','budget',),}),
        ) + super(CollaborationProjectAdmin, self).get_fieldsets(request, obj)


class StudentProjectAdmin(ProjectAdmin):

    def get_fieldsets(self, request, obj=None):
        #print("STP admin get fieldsets")
        return  (
        ('Student Project details', {
            'classes': ('collapse in',),
            'description': "Details for the overview table in the "
            "Annual Research Activity Report",
            'fields': ('level','organisation',),}),
        ) + super(StudentProjectAdmin, self).get_fieldsets(request, obj)
