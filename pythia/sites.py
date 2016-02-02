from __future__ import (unicode_literals, absolute_import)
from functools import update_wrapper
import os

from django.db.models.base import ModelBase
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from django.contrib import admin, messages
from django.conf import settings
from django.conf.urls.static import static as staticserve
from django.views import static
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


from pythia.admin import (AuditAdmin, UserAdmin, ProgramAdmin, DivisionAdmin,
    WorkCenterAdmin, AreaAdmin, RegionAdmin, DistrictAdmin)
from pythia.models import (User, Division, Program, WorkCenter, Area,
    Address, Region, District)
from pythia.documents.admin import (DocumentAdmin, ConceptPlanAdmin,
    ProjectPlanAdmin)
from pythia.documents.models import (ConceptPlan, ProjectPlan, ProgressReport,
    StudentReport, ProjectClosure)
from pythia.projects.admin import (ProjectAdmin, CollaborationProjectAdmin,
    StudentProjectAdmin, ProjectMembershipAdmin, ResearchFunctionAdmin)
from pythia.projects.models import (Project, ScienceProject,
    CoreFunctionProject, CollaborationProject, StudentProject,
    ProjectMembership, ResearchFunction)
from pythia.reports.admin import ARARReportAdmin
from pythia.reports.models import ARARReport
from pythia.views import (CommentUpdateView, comments_delete, comments_post,
        update_cache, arar_dashboard)
from pythia.models import Audit



class PythiaSite(admin.AdminSite):
    # login_template = "login.html" # replaced by login url

    def register(self, model_or_iterable, admin_class=None, **options):
        """Salvaged from deleted django-swingers AuditSite
        """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if issubclass(model, Audit):
                if not admin_class:
                    admin_class = AuditAdmin

            super(PythiaSite, self).register(model, admin_class, **options)

    def has_permission(self, request):
        return request.user.is_active

    def admin_view(self, view, cacheable=False):
        """
        This seems strange to be doing these checks on every page request, the
        checks only need to be done once on login. I wonder if there's a
        better place for these to go. Check `django.contrib.auth.forms`,
        there may be a hook for a post-login redirect url.
        """
        def inner(request, *args, **kwargs):
            if (not request.user.is_anonymous() and
                request.path != reverse('admin:logout',
                                        current_app=self.name)):
                user = request.user

                if user.is_external and not user.agreed:
                    return HttpResponseRedirect(
                        reverse('terms-and-conditions'))
                elif not user.is_staff:
                    return HttpResponseRedirect(
                        reverse('terms-and-conditions-agreed'))
                elif (not (user.first_name and user.last_name) and
                      request.path != reverse('admin:pythia_user_change',
                                              args=(request.user.pk,))):
                    # if first_name or last_name is empty, redirect to user
                    # profile
                    messages.add_message(
                        request, messages.WARNING,
                        'Please specify your first and last names')
                    return HttpResponseRedirect(
                        reverse('admin:pythia_user_change',
                                args=(request.user.pk,)))

            if ((not self.has_permission(request) and
                 request.path != reverse('admin:logout',
                                         current_app=self.name))):
                return self.login(request)
            return view(request, *args, **kwargs)
        if not cacheable:
            inner = never_cache(inner)
        # We add csrf_protect here so this function can be used as a utility
        # function for any view, without having to repeat 'csrf_protect'.
        if not getattr(view, 'csrf_exempt', False):
            inner = csrf_protect(inner)
        return update_wrapper(inner, view)

    def get_urls(self):
        from django.conf.urls import patterns, url, include

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns = patterns(
            '',
            url(r'^media/projects/(?P<path>.*)$',
                wrap(static.serve),
                {'document_root': os.path.join(settings.MEDIA_ROOT, 'projects')}),

            url(r'^media/profiles/(?P<path>.*)$',
                wrap(static.serve),
                {'document_root': os.path.join(settings.MEDIA_ROOT, 'profiles')}),

            url(r'^comments/delete/(\d+)/$',
                wrap(comments_delete),
                name='comments-delete'),

            url(r'^comments/post/$',
                wrap(comments_post),
                name='comments-post-comment'),

            url(r'^comments/edit/(?P<pk>\d+)/$',
                wrap(CommentUpdateView.as_view()),
                name='comments-edit'),

            # TODO: django_comments urls are not wrapped :(
            url(r'^comments/',
                include('django_comments.urls')),

            url(r'^action/update-cache/$',
                update_cache,
                name="update_cache"),

            url(r'^arar_dashboard',
                arar_dashboard,
                name="arar_dashboard"),
        ) + staticserve(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

        return urlpatterns + super(PythiaSite, self).get_urls()

site = PythiaSite()

# django stuff
site.register(User, UserAdmin)
site.register(Group, GroupAdmin)

# project stuff
site.register(Project, ProjectAdmin)
site.register(ScienceProject, ProjectAdmin)
site.register(CoreFunctionProject, ProjectAdmin)
site.register(CollaborationProject, CollaborationProjectAdmin)
site.register(StudentProject, StudentProjectAdmin)
site.register(ProjectMembership, ProjectMembershipAdmin)
site.register(ResearchFunction, ResearchFunctionAdmin)

# document stuff
site.register(ConceptPlan, ConceptPlanAdmin)
site.register(ProjectPlan, ProjectPlanAdmin)
site.register(ProgressReport, DocumentAdmin)
site.register(ProjectClosure, DocumentAdmin)
site.register(StudentReport, DocumentAdmin)

# reports
site.register(ARARReport, ARARReportAdmin)

# stuff
site.register(Division, DivisionAdmin)
site.register(Program, ProgramAdmin)
site.register(WorkCenter, WorkCenterAdmin)
site.register(Area, AreaAdmin)
site.register(Region, RegionAdmin)
site.register(District, DistrictAdmin)
# more stuff
site.register([Address])
