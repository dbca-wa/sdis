from django.conf import settings

def show_toolbar(request):
    """
    Determine when to show the debug toolbar. Only show if the server is in
    debug mode and the user has set the "debug" GET variable on a page.
    """
    if "debug" in request.GET:
        request.session['debug'] = request.GET['debug'] == "on"
    elif not "debug" in request.session:
        request.session['debug'] = False

    return settings.DEBUG and request.session['debug']
