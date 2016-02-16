from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

from pythia.sites import site
from pythia.views import TermsAndConditions, spell_check

js_info_dict = {'packages': ('django.conf',), }

urlpatterns = patterns(
    '',
    url(r'^jsi18n$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^select2/', include('django_select2.urls')),
    url(r'^spillchuck/$', spell_check),
    url(r'^terms/$', TermsAndConditions.as_view(), name='terms-and-conditions'),
    url(r'^terms-agreed/$',
        TemplateView.as_view(template_name="admin/terms-and-conditions-agreed.html"),
        name='terms-and-conditions-agreed'),
    url(r'^docs/dev/$',
        TemplateView.as_view(
            template_name="../../staticfiles/docs/dev/html/index.html"),
            name='dev-docs'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login',
        kwargs={'template_name': 'login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout',
        kwargs={'template_name': 'logout.html'}),
    url(r'', include(site.urls)),
    url(r'^$', 'pythia.views.home', name='homepage')
)

urlpatterns += staticfiles_urlpatterns()
