"""Pythia views.
"""
try:
    import json
except ImportError:
    from django.utils import simplejson as json

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic import edit
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


class DetailChangeList(ChangeList):
    def url_for_result(self, result):
        if self.model_admin.changelist_link_detail:
            pk = getattr(result, self.pk_attname)
            return reverse('admin:%s_%s_detail' % (self.opts.app_label,
                                                   self.opts.module_name),
                           args=(quote(pk),),
                           current_app=self.model_admin.admin_site.name)
        else:
            return super(DetailChangeList, self).url_for_result(result)


def arar_dashboard(request):
    from pythia.reports.models import ARARReport
    return TemplateResponse(request,
            'arar_dashboard/arar.html',
            {"original":ARARReport.objects.latest()})



@csrf_exempt
def update_cache(request):
    """Updates cached fields on Projects,
    guesses initials for Users without initials.
    """
    from pythia.projects.models import refresh_all_project_caches
    no_projects = refresh_all_project_caches()
    messages.success(request,
    "Team lists and areas updated for {0} projects".format(no_projects))

    from pythia.models import User
    [u.save() for u in User.objects.all()]
    no_users = User.objects.all().count()
    messages.success(request,
    "Missing initials guessed from first name for {0} users".format(no_users))

    return HttpResponseRedirect("/")

@csrf_exempt
def spell_check(request):
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
    #except Exception:
    #    logging.exception("Error running spellchecker")
    #    return HttpResponse("Error running spellchecker")
    return HttpResponse(json.dumps(output), content_type='application/json')


def comments_post(request):
    if not request.POST.get('comment'):
        return HttpResponseRedirect(request.REQUEST.get('next'))

    return post_comment(request)


def comments_delete(request, comment_id):
    comment = get_object_or_404(django_comments.get_model(), pk=comment_id,
            site__pk=settings.SITE_ID)
    context = {
        'next': request.GET.get('next'),
        'comment': comment,
        'is_popup': "_popup" in request.REQUEST
    }

    if request.method == 'POST':
        perform_delete(request, comment)
        if context['is_popup']:
            return render_to_response('admin/close_popup.html', context,
                    RequestContext(request))
        else:
            return next_redirect(request, fallback=request.GET.get('next') or
                    'comments-delete-done', c=comment.pk)

    else:
        return render_to_response('comments/delete.html', context,
                RequestContext(request))


class CommentUpdateForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('comment',)


class CommentUpdateView(edit.UpdateView):
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
            return render_to_response('admin/close_popup.html', {},
                    RequestContext(self.request))
        return super(CommentUpdateView, self).form_valid(form)


class TermsAndConditions(edit.FormView):
    template_name = "admin/terms-and-conditions.html"
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
