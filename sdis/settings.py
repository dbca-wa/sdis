from confy import database
import os
import sys
from unipath import Path

BASE_DIR = Path(__file__).ancestor(2)
PROJECT_DIR = os.path.join(BASE_DIR, 'pythia')
sys.path.insert(0, PROJECT_DIR)

root = lambda *x: os.path.join(BASE_DIR, *x)

SECRET_KEY = os.environ['SECRET_KEY'] if os.environ.get('SECRET_KEY', False) else 'foo'
DEBUG = True if os.environ.get('DEBUG', False) == 'True' else False
CSRF_COOKIE_SECURE = True if os.environ.get('CSRF_COOKIE_SECURE', False) == 'True' else False
SESSION_COOKIE_SECURE = True if os.environ.get('SESSION_COOKIE_SECURE', False) == 'True' else False

if not DEBUG:
    # Localhost, UAT and Production hosts
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
    ]
else:
    ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1', '::1']


# Application definition
SITE_TITLE = 'SDIS - Science Directorate Information System'
APPLICATION_VERSION_NO = '4.0'
SITE_ID = 1
SITE_NAME = 'SDIS'
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
    'django.contrib.postgres',
)

THIRD_PARTY_APPS = (
    'django_extensions',
    'django_comments', # replace with django-disqus
    'crispy_forms', # required?
    'smart_selects',
    'django_select2',
    'markup_deprecated',
    'guardian',
    'compressor', # set up correctly
    'mail_templated', # replace with envelope
    'envelope',
    'reversion',
    'rest_framework',
    'webtemplate_dpaw',
    'gunicorn', # replace with wsgiserver
    'django_wsgiserver',
    'django_nose',
)

DEBUG_APPS = (
    'debug_toolbar',
    'debug_toolbar_htmltidy',
    'django_pdb',
)

PROJECT_APPS = (
    'pythia',
    'pythia.documents',
    'pythia.projects',
    'pythia.reports',
)

INSTALLED_APPS += THIRD_PARTY_APPS
if DEBUG:
    INSTALLED_APPS += DEBUG_APPS
INSTALLED_APPS += PROJECT_APPS

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'reversion.middleware.RevisionMiddleware',
    # 'django.middleware.security.SecurityMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'dpaw_utils.middleware.SSOLoginMiddleware',
)

DEBUG_MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_pdb.middleware.PdbMiddleware',
)
if DEBUG:
    MIDDLEWARE_CLASSES += DEBUG_MIDDLEWARE


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                "django.core.context_processors.static",
                "django.core.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.core.context_processors.request",
                # "sdis.context_processors.standard",
            ],
        },
    },
]


# I8n
LANGUAGE_CODE = 'en-au'
TIME_ZONE = 'Australia/Perth'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DATE_FORMAT = '%d/%m/%Y'      # O5/10/2006
# Set the formats that will be accepted in date input fields
DATE_INPUT_FORMATS = (
    '%d/%m/%Y',             # '25/10/2006'
    '%Y-%m-%d',             # '2006-10-25'
    '%Y_%m_%d',             # '2006_10_25'
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


# User settings - enable SDIS custom user.
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
#   'pythia.backends.PythiaBackend',
)

ANONYMOUS_USER_ID = 100000
AUTH_USER_MODEL = 'pythia.User'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = LOGIN_URL
LOGOUT_URL = '/logout/'
LOGOUT_REDIRECT_URL = LOGOUT_URL

# Cache
# see http://django-select2.readthedocs.org/en/latest/django_select2.html
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    'select2': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# Set the cache backend to select2
SELECT2_CACHE_BACKEND = 'select2'

# Django-Restframework
REST_FRAMEWORK = {
# Use hyperlinked styles by default.
# Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS': 'rest_framework.serializers.HyperlinkedModelSerializer',

# Use Django's standard `django.contrib.auth` permissions,
# or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

# Misc settings
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'alerts.corporateict.domain')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 25)

# Envelope email
ENVELOPE_EMAIL_RECIPIENTS = ['sdis@DPaW.wa.gov.au']
ENVELOPE_USE_HTML_EMAIL = True

COMPRESS_ENABLED = False

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

DEBUG_TOOLBAR_CONFIG = {
    'HIDE_DJANGO_SQL': False,
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': 'sdis.utils.show_toolbar'
}

# Logging configuration
if not os.path.exists(os.path.join(BASE_DIR, 'logs')):
    os.mkdir(os.path.join(BASE_DIR, 'logs'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'precise': {
            'format': '{%(asctime)s.%(msecs)d}  %(message)s [%(levelname)s %(name)s]',
            'datefmt': '%H:%M:%S'
         },
        'standard': {
            'format': '%(asctime)s %(levelname)-8s [%(name)-15s] %(message)s',
            'datefmt': '%Y/%m/%d %H:%M:%S',
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
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
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(root('logs'), 'sdis.log'),
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
    # Set up logging differently to give us some more information about what's
    # going on
    LOGGING['loggers'] = {
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
    #TEMPLATE_LOADERS = (
    #    'django.template.loaders.filesystem.Loader',
    #    'django.template.loaders.app_directories.Loader',
    #)
