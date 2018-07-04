from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

from pythia.sites import site
from pythia.views import TermsAndConditions, spell_check
from pythia.api import router

js_info_dict = {'packages': ('django.conf',), }

urlpatterns = patterns(
    '',

    url(r'^jsi18n$', 'django.views.i18n.javascript_catalog', js_info_dict),

    url(r'^spillchuck/$', spell_check),

    url(r'^terms-and-conditions/$',
        TermsAndConditions.as_view(), name='terms-and-conditions'),

    url(r'^terms-and-conditions-agreed/$',
        TemplateView.as_view(template_name="admin/toc-agreed.html"),
        name='terms-and-conditions-agreed'),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),

    url(r'^api-docs/', include('rest_framework_swagger.urls')),

    # url(r'^export/(?P<model_name>[^/]+)/$',
    #     "django_tablib.views.generic_export"),

    url(r'', include(site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
