"""Base settings for SDIS dev and prod.

An environment variable `DEBUG` toggles dev and prod settings within this file.
Tests run by `fab test` explicitly use `sdis/test_settings.py`.
"""
from confy import env, database  # , cache
import ldap
import os
import sys
from unipath import Path

from django_auth_ldap.config import (LDAPSearch, GroupOfNamesType,
                                     LDAPSearchUnion)

BASE_DIR = Path(__file__).ancestor(2)
PROJECT_DIR = os.path.join(BASE_DIR, 'pythia')
sys.path.insert(0, PROJECT_DIR)

SECRET_KEY = env('SECRET_KEY', default='foo')
DEBUG = env('DEBUG', default=False)
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', default=True)
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', default=True)

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'sdis.dpaw.wa.gov.au',
    'sdis.dpaw.wa.gov.au.',
    'sdis-dev.dpaw.wa.gov.au',
    'sdis-dev.dpaw.wa.gov.au.',
    'sdis-test.dpaw.wa.gov.au',
    'sdis-test.dpaw.wa.gov.au.',
    'sdis-uat.dpaw.wa.gov.au',
    'sdis-uat.dpaw.wa.gov.au.',
    'static.dpaw.wa.gov.au'
    ]

INTERNAL_IPS = ['127.0.0.1', '::1']


# Application definition
SITE_ID = 1
SITE_URL = env('SITE_URL')
SITE_NAME = 'SDIS'
SITE_TITLE = 'Science Directorate Information System'
APPLICATION_VERSION_NO = '4.0'

DATABASES = {'default': database.config()}
ROOT_URLCONF = 'sdis.urls'
WSGI_APPLICATION = 'sdis.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.gis',
    # 'django.contrib.postgres',
    'django_extensions',
    'django_comments',
    'django_tablib',
    'compressor',

    'crispy_forms',
    'smart_selects',
    'django_select2',
    'markup_deprecated',
    'guardian',

    'mail_templated',
    'reversion',
    'rest_framework',

    'leaflet',
    'south',
    'gunicorn',
    'django_wsgiserver',

    'pythia',
    'pythia.documents',
    'pythia.projects',
    'pythia.reports',
    )

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'dpaw_utils.middleware.SSOLoginMiddleware',
    # loaded if DEBUG (below):
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'django_pdb.middleware.PdbMiddleware'
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.core.context_processors.static',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    )


# I8n
LANGUAGE_CODE = 'en-au'
TIME_ZONE = 'Australia/Perth'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DATE_FORMAT = 'd/m/Y'      # O5/10/2006
# Set the formats that will be accepted in date input fields
DATE_INPUT_FORMATS = (
    'd/m/Y',             # '25/10/2006'
    'Y-m-d',             # '2006-10-25'
    'Y_m_d',             # '2006_10_25'
    )


# Uploads
if not os.path.exists(os.path.join(BASE_DIR, 'media')):
    os.mkdir(os.path.join(BASE_DIR, 'media'))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Static files (CSS, JavaScript, Images)
if not os.path.exists(os.path.join(BASE_DIR, 'staticfiles')):
    os.mkdir(os.path.join(BASE_DIR, 'staticfiles'))
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(PROJECT_DIR, 'static'),)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    )
# This is required to add context variables to all templates:
STATIC_CONTEXT_VARS = {}

COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader',
     ('django.template.loaders.filesystem.Loader',
      'django.template.loaders.app_directories.Loader',)),
    )

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'pythia/templates'),)

# User settings - enable Persona and SDIS custom user.
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'pythia.backends.PythiaBackend',
    'pythia.backends.EmailBackend',
    )

ANONYMOUS_USER_ID = 100000
AUTH_USER_MODEL = 'pythia.User'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = LOGIN_URL
LOGOUT_URL = '/logout/'
LOGOUT_REDIRECT_URL = LOGOUT_URL

# LDAP settings
AUTH_LDAP_SERVER_URI = env('LDAP_SERVER_URI')
AUTH_LDAP_BIND_DN = env('LDAP_BIND_DN')
AUTH_LDAP_BIND_PASSWORD = env('LDAP_BIND_PASSWORD')

AUTH_LDAP_ALWAYS_UPDATE_USER = False
AUTH_LDAP_AUTHORIZE_ALL_USERS = True
AUTH_LDAP_FIND_GROUP_PERMS = False
AUTH_LDAP_MIRROR_GROUPS = False
AUTH_LDAP_CACHE_GROUPS = False
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300

AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
    LDAPSearch("DC=corporateict,DC=domain", ldap.SCOPE_SUBTREE,
               "(sAMAccountName=%(user)s)"),
    LDAPSearch("DC=corporateict,DC=domain", ldap.SCOPE_SUBTREE,
               "(mail=%(user)s)"),
               )

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "DC=corporateict,DC=domain",
    ldap.SCOPE_SUBTREE, "(objectClass=group)"
    )

AUTH_LDAP_GLOBAL_OPTIONS = {
    ldap.OPT_X_TLS_REQUIRE_CERT: False,
    ldap.OPT_REFERRALS: False,
    }

AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")

AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': "givenName",
    'last_name': "sn",
    'email': "mail",
    }


# Django-Restframework
REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES':
        ['rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly']
    }

# Email
EMAIL_HOST = env('EMAIL_HOST', default='email.host')
EMAIL_PORT = env('EMAIL_PORT', default=25)
ENVELOPE_EMAIL_RECIPIENTS = ['sdis@DPaW.wa.gov.au']
ENVELOPE_USE_HTML_EMAIL = True
DEFAULT_FROM_EMAIL = '"SDIS" <sdis-noreply@dpaw.wa.gov.au>'


COMPRESS_ENABLED = True

DEBUG_TOOLBAR_CONFIG = {
    'HIDE_DJANGO_SQL': False,
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': 'sdis.utils.show_toolbar'
    }

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)-.19s [%(process)d] [%(levelname)s] '
                      '%(message)s'
                      },
            },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
            },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
            },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/sdis.log'),
            'formatter': 'standard',
            'maxBytes': '16777216'
            },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            }
        },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
            },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
            },
        'sdis': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
            }
        }
    }


if DEBUG:
    ALLOWED_HOSTS = ['*']

    COMPRESS_ENABLED = False

    INSTALLED_APPS += (
        'debug_toolbar',
        'debug_toolbar_htmltidy',
        'django_pdb',
        )

    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'django_pdb.middleware.PdbMiddleware',
        )

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    LOGGING['loggers'] = {
        'django_auth_ldap': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True
            },
        'django_browserid': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True
            },
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True
            },
        'sdis': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
            },
        }

    # SDIS-260: cached template loader crashes debug toolbar template source
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        )
