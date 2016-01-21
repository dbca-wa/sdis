from django.conf import settings


def persona(request):
    return {
        'PERSONA_LOGIN': settings.PERSONA_LOGIN
    }
