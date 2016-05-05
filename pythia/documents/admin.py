from __future__ import unicode_literals, absolute_import

from django.contrib.admin.util import unquote
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.forms import fields_for_model
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from pythia.admin import BaseAdmin, Breadcrumb, DownloadAdminMixin

# from pythia.documents.models import Document
# from pythia.models import User
from pythia.templatetags.pythia_base import pythia_urlname
from pythia.utils import mail_from_template, snitch

from diff_match_patch import diff_match_patch
from django_fsm import can_proceed
from functools import update_wrapper
from reversion.models import Version
from sdis import settings

class DocumentAdmin(BaseAdmin, DownloadAdminMixin):
    """
    Add some additional functionality to documents.

     - Lock the document after approval.
     - Allow users to transition the document between the various document
       states.
     - Display the differences between previous versions of the document.

    All document types should inherit from this ModelAdmin, or use it
    directly.
    """
    exclude = ('project', 'status')
    list_display = (
        'project_id', '__str__', 'project_title',
        'project_type', 'project_year', 'project_number',
        'project_owner', 'program', 'status')
    list_display_links = ('project_id', '__str__')

    # A few aux methods for list_display
    def project_id(self, obj):
        return obj.project.project_year_number
    project_id.short_description = 'ID'

    def project_title(self, obj):
        return obj.project.project_title_html
    project_title.short_description = 'Project Name'
    project_title.admin_order_field = 'title'
    project_title.allow_tags = True

    def project_owner(self, obj):
        return obj.project.project_owner.get_full_name()
    project_owner.short_description = 'Supervising Scientist'
    project_owner.admin_order_field = 'project__project_owner__last_name'

    def project_type(self, obj):
        return obj.project.get_type_display()
    project_type.short_description = 'Project Type'
    project_type.admin_order_field = 'project__type'

    def project_year(self, obj):
        return obj.project.year
    project_year.short_description = 'Project Year'
    project_year.admin_order_field = 'project__year'

    def project_number(self, obj):
        return obj.project.number
    project_number.short_description = 'Project Number'
    project_year.admin_order_field = 'project__year'

    def program(self, obj):
        return obj.project.program
    program.short_description = 'Program'
    program.admin_order_field = 'project__program__cost_center'
    # end list_display crutches

    @property
    def download_template(self):
        return "doc_"+self.model._meta.model_name

    def get_readonly_fields(self, request, obj=None):
        """Lock the document after seeking approval for all but superusers."""
        if (obj and obj.is_nearly_approved and not request.user.is_superuser):
            return fields_for_model(obj, exclude=self.exclude).keys()
        return super(DocumentAdmin, self).get_readonly_fields(request, obj)

    def get_breadcrumbs(self, request, obj=None, add=False):
        """
        Override the base breadcrumbs to add the project list to the trail.
        """
        return (
            Breadcrumb(_('Home'), reverse('admin:index')),
            Breadcrumb(_('All projects'),
                       reverse('admin:projects_project_changelist')))

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
            url(r'^(.+)/endorsement/$', wrap(self.endorsement_view),
                name='%s_%s_endorsement' % info),
            url("^([^/]+)/history/([^/]+)/diff$", wrap(self.diff_view),
                name='%s_%s_diff' % info),)
        return extra_urls + super(BaseAdmin, self).get_urls()

    def transition_view(self, request, object_id, extra_context=None):
        """
        Transition a project or document through its lifecycle.

        Raise 403 forbidden if it is not possible to perform this action (
        lack of permission, transition not allowed).
        """
        model = self.model
        opts = model._meta
        obj = self.get_object(request, unquote(object_id))
        tx = request.GET.get('transition')

        # Does the thing exists
        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does '
                            'not exist.') % {
                                'name': force_text(opts.verbose_name),
                                'key': escape(object_id)})

        # Is current user allowed to do the stuff with the thing
        # Should we use django_fsm.can_proceed instead?
        if tx not in [t.name for t in
                      obj.get_available_user_status_transitions(request.user)]:
            print("Requested transition '{0}' not available for the "
                  "current user {1}".format(tx, request.user))
            raise PermissionDenied

        t = [t for t in obj.get_available_user_status_transitions(request.user)
             if t.name == tx][0]

        if request.method == 'POST':
            # Then do the stuff with the thing
            print("About to run transition {0}, object status {1}".format(
                t.name, obj.status))
            getattr(obj, t.name)()
            obj.save()
            print("Finished running transition {0}, object status {1}".format(
                t.name, obj.status))

            # Email notifications
            if ('_notify' in request.POST) and (
                    request.POST.get('_notify') == u'on'):

                recipients = obj.get_users_to_notify(t.name)
                recipients.discard(request.user)
                if settings.DEBUG:
                    print("[DEBUG] recipients would have been: {0}".format(
                       recipients))
                    User = get_user_model()
                    recipients = [User.objects.get(username='florianm'), ]
                    print("[DEBUG] recipients replaced with: {0}".format(
                       recipients))

                context = {
                    'instigator': request.user,
                    'object_name': '{0} of {1}'.format(
                        obj.__str__(), obj.project.fullname),
                    'object_url': request.build_absolute_uri(reverse(
                        pythia_urlname(obj.opts, 'change'), args=[obj.pk])),
                    'action': t.name,
                    'status': t.target,
                    }
                mail_from_template(
                    '{0} has been updated'.format(
                        obj.project.project_type_year_number),
                    list(recipients), 'email/email_base', context)

            # Redirect the user back to the document change page
            redirect_url = reverse('admin:%s_%s_change' %
                                   (opts.app_label, opts.model_name),
                                   args=(object_id,),
                                   current_app=self.admin_site.name)
            return HttpResponseRedirect(redirect_url)

        context = dict(
            title=_('%s: %s') % (t.custom["verbose"], force_text(obj)),
            breadcrumbs=self.get_breadcrumbs(request, obj),
            transition_name=capfirst(force_text(t.name)),
            model_name=capfirst(force_text(opts.verbose_name_plural)),
            object=obj,
            opts=opts,)
        context.update(extra_context or {})

        return TemplateResponse(request, [
            "admin/%s/%s/%s_transition.html" % (
                opts.app_label, opts.model_name, t.name),
            "admin/%s/%s/transition.html" % (opts.app_label, opts.model_name),
            "admin/%s/%s_transition.html" % (opts.app_label, t.name),
            "admin/%s/transition.html" % opts.app_label
            ], context, current_app=self.admin_site.name)

    def endorsement_view(self, request, object_id, extra_context=None):
        """
        Handle adding an endorsement to a document. For an endorsement to be
        added, the document must be in review. An endorsement indicates that
        a review is happy with the state of the document as written.
        """
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does '
                            'not exist.') % {
                                'name': force_text(opts.verbose_name),
                                'key': escape(object_id)})

        context = dict(
            title=_('Add endorsement: %s') % force_text(obj),
            breadcrumbs=self.get_breadcrumbs(request, obj),
            model_name=capfirst(force_text(opts.verbose_name_plural)),
            object=obj,
            opts=opts,
        )
        context.update(extra_context or {})
        return TemplateResponse(request, [
            "admin/%s/%s/endorsement.html" % (
                opts.app_label, opts.model_name),
            "admin/%s/endorsement.html" % opts.app_label,
            "admin/endorsement.html"
        ], context, current_app=self.admin_site.name)

    def history_view(self, request, object_id, extra_context=None):
        obj = get_object_or_404(self.model, pk=unquote(object_id))

        context = {
            'has_diff_view': True,
            'breadcrumbs': self.get_breadcrumbs(request, obj)
        }
        context.update(extra_context or {})
        return super(DocumentAdmin, self).history_view(request, object_id,
                                                       extra_context=context)

    # This view is in serious need of a refactor now that we are no longer
    # using TextContext and TableContexts or GFKs. Write some tests!
    # I have removed some offending code -- search the history of this
    # repository. Remove this comment when all is good in the world of diff.
    def diff_view(self, request, object_id, version_id, extra_context=None):
        """
        Generate a diff between document versions.
        """
        opts = self.model._meta
        app_label = opts.app_label

        obj = get_object_or_404(self.model, pk=unquote(object_id))
        obj_old = get_object_or_404(Version, pk=unquote(version_id),
                                    object_id=force_text(obj.pk))

        fieldsets = self.get_fieldsets(request, obj)
        inline_instances = self.get_inline_instances(request, obj)

        d = diff_match_patch()
        diffs = []

        for (name, field_options) in fieldsets:
            if 'fields' in field_options:
                for f in field_options['fields']:
                    field = getattr(obj, f)
                    if (not field) or (type(field) not in (str, unicode)):
                        continue
                    diff = d.diff_main( obj_old.field_dict[f] or '',
                            field)
                    d.diff_cleanupSemantic(diff)
                    diffs.append((opts.get_field_by_name(f)[0].verbose_name,
                            mark_safe(d.diff_prettyHtml(diff))))


        context = {
            'breadcrumbs': self.get_breadcrumbs(request, obj),
            'diffs': diffs, 'object': obj, 'opts': self.model._meta,
            'version_date': obj_old.revision.date_created,
        }
        context.update(extra_context or {})

        return TemplateResponse(request, self.object_diff_template or [
            'admin/%s/%s/object_diff.html' % (app_label,
                                              opts.object_name.lower()),
            'admin/%s/object_diff.html' % app_label,
            'admin/object_diff.html'
        ], context, current_app=self.admin_site.name)


class ConceptPlanAdmin(DocumentAdmin):
    def summary(self, obj):
        return mark_safe(obj.summary)
    summary.allow_tags = True


class ProjectPlanAdmin(DocumentAdmin):
   def get_readonly_fields(self, request, obj=None):
    """
    Lock the document after approval. Allow super-users to edit it after
    clicking a link that sets a GET variable. If a super user makes a POST
    request, it should be allowed.
    """

    if (obj and not obj.is_approved and not (request.user.is_superuser or
            request.user in Group.objects.get(name='SMT').user_set.all() or
            request.user in Group.objects.get(name='SCD').user_set.all() or
            request.user in Group.objects.get(name='BM').user_set.all() or
            request.user in Group.objects.get(name='HC').user_set.all() or
            request.user in Group.objects.get(name='AE').user_set.all() or
            request.user in Group.objects.get(name='DM').user_set.all())):
        return ('bm_endorsement', 'hc_endorsement', 'ae_endorsement')

    # if is_approved: all readonly except for superuser
    elif (obj and obj.is_approved and not request.user.is_superuser):
        return fields_for_model(obj, exclude=self.exclude).keys()

    else:
        return super(ProjectPlanAdmin, self).get_readonly_fields(request, obj)
