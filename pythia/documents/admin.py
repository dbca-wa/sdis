"""pythia.documents Admin."""
from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.admin.util import unquote
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.forms import fields_for_model
from django.http import Http404
from django.http import HttpResponseRedirect  # HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from mail_templated import send_mail

from pythia.admin import BaseAdmin
from pythia.admin import Breadcrumb
from pythia.admin import DownloadAdminMixin

# from pythia.documents.models import Document
# from pythia.models import User
from pythia.templatetags.pythia_base import pythia_urlname
from sdis import settings

from diff_match_patch import diff_match_patch
# from django_fsm import can_proceed
from functools import update_wrapper
from reversion.models import Version

import logging

logger = logging.getLogger(__name__)


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
        """Return project_year_number as ID."""
        return obj.project.project_year_number
    project_id.short_description = 'ID'

    def project_title(self, obj):
        """Return project_title_html as title."""
        return obj.project.project_title_html
    project_title.short_description = 'Project Name'
    project_title.admin_order_field = 'title'
    project_title.allow_tags = True

    def project_owner(self, obj):
        """Return project_owner fullname as Supervising Scientist."""
        return obj.project.project_owner.get_full_name()
    project_owner.short_description = 'Supervising Scientist'
    project_owner.admin_order_field = 'project__project_owner__last_name'

    def project_type(self, obj):
        """Return project_type as Project Type."""
        return obj.project.get_type_display()
    project_type.short_description = 'Project Type'
    project_type.admin_order_field = 'project__type'

    def project_year(self, obj):
        """Return project_year as Project Year."""
        return obj.project.year
    project_year.short_description = 'Project Year'
    project_year.admin_order_field = 'project__year'

    def project_number(self, obj):
        """Return project_number as Project Number."""
        return obj.project.number
    project_number.short_description = 'Project Number'
    project_year.admin_order_field = 'project__year'

    def program(self, obj):
        """Return program as Program."""
        return obj.project.program
    program.short_description = 'Program'
    program.admin_order_field = 'project__program__cost_center'
    # end list_display crutches

    @property
    def download_template(self):
        """Derive a download template name from model name."""
        return "doc_" + self.model._meta.model_name

    def get_readonly_fields(self, request, obj=None):
        """Lock the document after seeking approval for all but superusers."""
        try:
            logger.debug("{0} views {1}".format(request.user.fullname, obj))
        except:
            logger.debug("DocumentAdmin called without object or request.")

        if obj and request.user.is_superuser:
            return ()
        elif obj and request.user in obj.get_users_with_change_permissions():
            return super(DocumentAdmin, self).get_readonly_fields(request, obj)
        else:
            return fields_for_model(obj, exclude=self.exclude).keys()

    def get_urls(self):
        """Add transition/endorsement/diff views URLs."""
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
            # url(r'^(.+)/endorsement/$', wrap(self.endorsement_view),
            #     name='%s_%s_endorsement' % info),
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

        # Does the thing exist
        if obj is None:
            msg = _('Object %(name)s with PK %(key)r does not exist.') % {
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

        # Is the tx available to the current user?
        if tx not in [t.name for t in
                      obj.get_available_user_status_transitions(request.user)]:
            logger.warning("Requested transition '{0}' not available for the "
                           "current user {1}".format(tx, request.user.fullname))
            raise PermissionDenied

        # Is there a better way to get the transition object?
        t = [t for t in obj.get_available_user_status_transitions(request.user)
             if t.name == tx][0]

        # Who should get notified about this tx?
        recipients = obj.get_users_to_notify(t.target)
        recipients_text = ", ".join([r.fullname for r in recipients])
        explanation = t.custom["explanation"].format(recipients_text)
        # recipients.discard(request.user)

        # We'll use the context to populate both email and transition.html page
        context = dict(
            instigator=request.user,
            object_name=force_text(obj),
            object_url=request.build_absolute_uri(reverse(
                pythia_urlname(obj.opts, 'change'), args=[obj.pk])),
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
            do_notify = '_notify' in request.POST and request.POST.get(
                '_notify') == u'on'
            tmpl = 'email/email_base.tpl'
            to_emails = [u.email for u in recipients]
            from_email = settings.DEFAULT_FROM_EMAIL
            if do_notify:
                send_mail(tmpl, context, from_email, to_emails)

            # Redirect the user back to the document change page
            redirect_url = reverse(
                'admin:%s_%s_change' % (opts.app_label, opts.model_name),
                args=(object_id,), current_app=self.admin_site.name)
            return HttpResponseRedirect(redirect_url)

        return TemplateResponse(request, [
            "admin/%s/%s/%s_transition.html" % (
                opts.app_label, opts.model_name, t.name),
            "admin/%s/%s/transition.html" % (opts.app_label, opts.model_name),
            "admin/%s/%s_transition.html" % (opts.app_label, t.name),
            "admin/%s/transition.html" % opts.app_label
        ], context, current_app=self.admin_site.name)

    # def endorsement_view(self, request, object_id, extra_context=None):
    #     """Handle adding an endorsement to a document.
    #
    #     For an endorsement to be added, the document must be in review.
    #     An endorsement indicates that a review is happy with the state of the
    #     document as written.
    #     """
    #     model = self.model
    #     opts = model._meta
    #
    #     obj = self.get_object(request, unquote(object_id))
    #
    #     if obj is None:
    #         raise Http404(_('%(name)s object with primary key %(key)r does '
    #                         'not exist.') % {
    #                             'name': force_text(opts.verbose_name),
    #                             'key': escape(object_id)})
    #
    #     context = dict(
    #         title=_('Add endorsement: %s') % force_text(obj),
    #         breadcrumbs=self.get_breadcrumbs(request, obj),
    #         model_name=capfirst(force_text(opts.verbose_name_plural)),
    #         object=obj,
    #         opts=opts,
    #         )
    #     context.update(extra_context or {})
    #     return TemplateResponse(request, [
    #         "admin/%s/%s/endorsement.html" % (
    #             opts.app_label, opts.model_name),
    #         "admin/%s/endorsement.html" % opts.app_label,
    #         "admin/endorsement.html"
    #         ], context, current_app=self.admin_site.name)

    def history_view(self, request, object_id, extra_context=None):
        """History view."""
        obj = get_object_or_404(self.model, pk=unquote(object_id))

        try:
            logger.debug("{0} views history_view of {1}".format(
                request.user.fullname, obj))
        except:
            logger.debug("DocumentAdmin history_view called "
                         "without object or request.")

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
        """Generate a diff between document versions."""
        opts = self.model._meta
        app_label = opts.app_label

        obj = get_object_or_404(self.model, pk=unquote(object_id))
        obj_old = get_object_or_404(
            Version, pk=unquote(version_id), object_id=force_text(obj.pk))

        try:
            logger.debug("{0} views diff_view of {1}".format(
                request.user.fullname, obj))
        except:
            logger.debug("DocumentAdmin diff_view called without "
                         "object or request.")

        fieldsets = self.get_fieldsets(request, obj)
        # inline_instances = self.get_inline_instances(request, obj)

        d = diff_match_patch()
        diffs = []

        for (name, field_options) in fieldsets:
            if 'fields' in field_options:
                for f in field_options['fields']:
                    field = getattr(obj, f)
                    if (not field) or (type(field) not in (str, unicode)):
                        continue
                    diff = d.diff_main(obj_old.field_dict[f] or '', field)
                    d.diff_cleanupSemantic(diff)
                    diffs.append((
                        opts.get_field_by_name(f)[0].verbose_name,
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
    """Custom ConceptPlan Admin."""

    def summary(self, obj):
        """Experiment: mark field `summary` safe for HTML content."""
        return mark_safe(obj.summary)
    summary.allow_tags = True

    # def get_readonly_fields(self, request, obj=None):
    #     """Custom logic to toggle editing of ConnceptPlan fields.

    #     Inject logging message.
    #     """
    #     try:
    #         logger.debug("{0} views {1}".format(request.user.fullname, obj))
    #     except:
    #         logger.debug("ConceptPlanAdmin called without object or request.")

    #     return super(ConceptPlanAdmin, self).get_readonly_fields(request, obj)


class ProjectPlanAdmin(DocumentAdmin):
    """Custom ProjectPlan Admin.

    Editing of endorsement fields is restricted to special roles.
    """

    def get_readonly_fields(self, request, obj=None):
        """Custom logic to toggle editing of ProjectPlan fields.

        Logic in sequential order:

        * Superusers and special roles can always edit.
        * If document is not approved yet, and users has change permission,
          then the user can edit all fields except endorsements.
        * Approved SPPs are read-only.
        * All other cases, e.g. users without change permissions,
          default to DocumentAdmin.get_readonly_fields.
        """
        special_user = obj and request.user and (
            request.user.is_superuser or
            request.user in obj.project.special_roles)

        if special_user:
            # Superusers and special roles can always edit SPPs
            logger.debug("ProjectPlan admin: editable for special user.")
            return ()

        elif (obj and not obj.is_approved and request.user and
              request.user in obj.get_users_with_change_permissions()):
            # Normal users can edit doc if not approved except endorsements
            logger.debug("ProjectPlan admin: non approved = editable except "
                         "endorsements for team member.")
            return ('bm_endorsement', 'hc_endorsement', 'ae_endorsement')

        # if is_approved: all readonly
        elif (obj and obj.is_approved):
            logger.debug("ProjectPlan admin: approved = read-only "
                         "for normal user.")
            return fields_for_model(obj, exclude=self.exclude).keys()

        else:
            logger.debug("ProjectPlan admin: defaulting to DocumentAdmin.")
            return super(ProjectPlanAdmin, self).get_readonly_fields(
                request, obj)
