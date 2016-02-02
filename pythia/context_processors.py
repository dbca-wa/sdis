from django.conf import settings

def template_context(request):
    """Pass extra context variables to every template.
    """
    context = {
        'site_title': settings.APPLICATION_TITLE,
        # 'site_acronym': settings.APPLICATION_ACRONYM,
        'version_no': settings.APPLICATION_VERSION_NO,
        # 'geoserver_wms_url': settings.GEOSERVER_WMS_URL,
        # 'geoserver_wfs_url': settings.GEOSERVER_WFS_URL,
        # 'geocoder_url': settings.GEOCODER_URL,
    }
    context['superuser'] = request.user.is_superuser()
    # if request.user.is_authenticated():
        # stuff
    context.update(settings.STATIC_CONTEXT_VARS)
    return context
