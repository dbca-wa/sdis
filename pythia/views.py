"""Custom pythia views."""

import json
import logging

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic import edit, ListView
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.util import quote

import django_comments
from django_comments.models import Comment
from django_comments.views.comments import post_comment
from django_comments.views.moderation import perform_delete
from django_comments.views.utils import next_redirect

from pythia.forms import TermsAndConditionsForm
from pythia.models import Division
from pythia.projects.models import Project
from pythia.projects.filters import ProjectFilter

logger = logging.getLogger(__name__)


class DetailChangeList(ChangeList):
    """Custom DetailChangeList."""

    def url_for_result(self, result):
        """URL for result."""
        if self.model_admin.changelist_link_detail:
            pk = getattr(result, self.pk_attname)
            return reverse('admin:%s_%s_detail' % (self.opts.app_label,
                                                   self.opts.module_name),
                           args=(quote(pk),),
                           current_app=self.model_admin.admin_site.name)
        else:
            return super(DetailChangeList, self).url_for_result(result)


def arar_dashboard(request):
    """Render ARAR dashboard with latest ARAR."""
    from pythia.reports.models import ARARReport
    logger.info("User {0} views ARAR Dashboard".format(request.user))

    return TemplateResponse(
        request,
        'arar_dashboard/arar.html',
        {"original": ARARReport.objects.latest()})


def project_dashboard(request):
    """Render Projects grouped by Programs.

    If no request user is given, return Projects of the first available Division.
    If the user is a superuser, return all Projects of all Divisions.
    If the user is not a superuser, return Projects of the User's Division.

    User.division is a proxy for User.program.division with a fallback to the 
    first available Division.
    """
    if request.user:
        logger.info("User {0} views Project Dashboard".format(request.user))
    else:
        logger.info("User (not available) views Project Dashboard")

    division = request.user.division

    # if request.user.is_superuser:
    # # This throws ISE on program change_url: program.opts.model_name not found
    #     projects = Project.objects.order_by(
    #         'program__position',
    #         'position',
    #         '-year',
    #         '-number'
    #     ).prefetch_related(
    #         'program',
    #         'program__modifier',
    #         'program__program_leader'
    #     )
    # else:
    projects = Project.objects.filter(
        effective_to__isnull=True,
        program__division=division
    ).order_by(
        'program__position',
        'position',
        '-year',
        '-number'
    ).prefetch_related(
        'program',
        'program__modifier',
        'program__program_leader'
    )

    return TemplateResponse(
        request,
        'projects/dashboard.html',
        {
            "division": division,
            "projects": projects
        }
    )


class ProjectList(ListView):
    """A ListView of Projects of a User's Division.

    Superusers are also limited to their own Division.
    
    User.division is a proxy for User.program.division with a fallback to the 
    first available Division.

    In the future, the Division-based filtering could become a pre-selected filter
    rather than a hard limit of visibility.
    """
    model = Project
    template = "projects/project_list.html"
    filter_class = ProjectFilter

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProjectList, self).get_context_data(**kwargs)
        context['division'] = self.request.user.division if self.request.user else Division.objects.first()
        context['show_all_divisions'] = self.request.user.is_admin if self.request.user else True
        context['list_filter'] = ProjectFilter(
            self.request.GET, queryset=self.get_queryset())
        return context

    def get_queryset(self):
        """Return Projects filtered to a Division depending on User role.

        * Anonymous users: Projects of all Divisions.
        * Admin users: Projects of all Divisions.
        * Non-admin users: Projects of own Division only.
        """
        qs = super(ProjectList, self).get_queryset(
                ).filter(
                    effective_to__isnull=True
                ).prefetch_related(
                    'program',
                    'program__division',
                    'program__modifier',
                    'program__program_leader'
                ).order_by(
                    'program__position',
                    'position',
                    '-year',
                    '-number'
                )
        
        if self.request.user and not self.request.user.is_admin:
            qs = qs.filter(program__division=self.request.user.division)

        logger.info(
            "User {0} views Project Dashboard: Division {1}".format(
                self.request.user, 
                self.request.user.division.slug if self.request.user else "(Anonymous user)"
            )
        )

        return ProjectFilter(self.request.GET, queryset=qs).qs


@csrf_exempt
def update_cache(request):
    """Update cached fields on Projects, guess initials for Users without."""
    from pythia.projects.models import refresh_all_project_caches
    no_projects = refresh_all_project_caches()
    messages.success(
        request,
        "Team lists and areas updated for {0} projects".format(no_projects))

    from pythia.models import User
    [u.save() for u in User.objects.all()]
    no_users = User.objects.all().count()
    messages.success(
        request,
        "Missing initials guessed from first name for {0} users".format(
            no_users))

    from pythia.documents.utils import grant_special_role_permissions
    grant_special_role_permissions()
    messages.success(
        request,
        "Granted projectplan edit privileges to special roles.")

    return HttpResponseRedirect("/")


@csrf_exempt
def batch_approve_progressreports(request):
    """Approve all progress reports that are in approval.

    This is handy to close off an ARAR cycle.
    """
    if not request.user.is_superuser:
        messages.error(request,
                       "Only superusers can batch-approve ProgressReports!")
        return HttpResponseRedirect("/")

    from pythia.documents.models import (
        Document, ProgressReport, StudentReport)

    pr = [[d.approve(), d.save()] for d in
          ProgressReport.objects.filter(status=Document.STATUS_INAPPROVAL)]
    sr = [[d.approve(), d.save()] for d in
          StudentReport.objects.filter(status=Document.STATUS_INAPPROVAL)]

    messages.success(
        request,
        "Batch-approved {0} ProgressReports and {1} StudentReports".format(
            len(pr), len(sr)))

    return HttpResponseRedirect("/")


@csrf_exempt
def spell_check(request):
    """Spellcheck view."""
    import enchant

    raw = request.body
    input = json.loads(raw)
    id = input['id'] if ('id' in input) else None
    method = input['method'] if ('method' in input) else {}
    params = input['params'] if ('params' in input) else {}

    result = {}

    try:
        if params and method:
            lang = params['lang'] if ('lang' in params) else 'en-au'
            arg = params['words'] if ('words' in params) else []

            if not enchant.dict_exists(str(lang)):
                raise RuntimeError(
                    "dictionary not found for language '%s'" % lang)

            checker = enchant.Dict(str(lang))

            if method == 'spellcheck':
                for x in [word for word in arg if word and not
                          checker.check(word)]:
                    result[x] = checker.suggest(x)

    except Exception:
        pass

    output = {
        'id': id,
        'result': result,
    }
    # except Exception:
    #    logging.exception("Error running spellchecker")
    #    return HttpResponse("Error running spellchecker")
    return HttpResponse(json.dumps(output), content_type='application/json')


def comments_post(request):
    """Post comment view."""
    if not request.POST.get('comment'):
        return HttpResponseRedirect(request.REQUEST.get('next'))

    return post_comment(request)


def comments_delete(request, comment_id):
    """Delete comment view."""
    comment = get_object_or_404(django_comments.get_model(),
                                pk=comment_id,
                                site__pk=settings.SITE_ID)
    context = {
        'next': request.GET.get('next'),
        'comment': comment,
        'is_popup': "_popup" in request.REQUEST
    }

    if request.method == 'POST':
        perform_delete(request, comment)
        if context['is_popup']:
            return render_to_response(
                'admin/close_popup.html', context, RequestContext(request))
        else:
            return next_redirect(
                request,
                fallback=request.GET.get('next') or 'comments-delete-done',
                c=comment.pk)

    else:
        return render_to_response(
            'comments/delete.html', context, RequestContext(request))


class CommentUpdateForm(ModelForm):
    """Custom comment update form."""

    class Meta:
        model = Comment
        fields = ('comment',)


class CommentUpdateView(edit.UpdateView):
    """Custom comment update view."""

    model = Comment
    template_name = "comments/comment_form.html"
    form_class = CommentUpdateForm

    def get_context_data(self, **kwargs):
        context = {
            'next': self.request.REQUEST.get('next'),
            'is_popup': self.request.REQUEST.get('_popup')
        }
        context.update(kwargs)
        return super(CommentUpdateView, self).get_context_data(**context)

    def get_success_url(self):
        return self.request.REQUEST.get(
            'next', super(CommentUpdateView, self).get_success_url())

    def form_valid(self, form):
        if self.request.REQUEST.get('_popup'):
            return render_to_response(
                'admin/close_popup.html', {}, RequestContext(self.request))
        return super(CommentUpdateView, self).form_valid(form)


class TermsAndConditions(edit.FormView):
    """Custom TermsAndConditions view."""
    template_name = "admin/toc.html"
    form_class = TermsAndConditionsForm

    def get_success_url(self):
        return reverse('terms-and-conditions-agreed')

    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.agreed = True
        user.save()

        """
        mail_admins("A new user has registered and agreed to the terms "
                    "and conditions.",
                    "A new user has registered and agreed to the terms "
                    "and conditions. "
                    "They are waiting for their account to be unlocked.")
        """
        return super(TermsAndConditions, self).form_valid(form)
