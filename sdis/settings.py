from confy import database
import ldap
import os

#from django_auth_ldap.config import (LDAPSearch, GroupOfNamesType, LDAPSearchUnion)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
root = lambda *x: os.path.join(BASE_DIR, *x) 
sys.path.insert(0, root('apps'))

SECRET_KEY = os.environ['SECRET_KEY'] if os.environ.get('SECRET_KEY', False) else 'foo'

DEBUG = True if os.environ.get('DEBUG', False) == 'True' else False
TEMPLATE_DEBUG = DEBUG
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

# Application definition
SITE_TITLE = 'SDIS - Science Directorate Information System'
APPLICATION_VERSION_NO = '4.0'
SITE_ID = 1
#SITE_URL = os.environ.get('SITE_URL', None)
SITE_NAME = 'SDIS'

    #'django_browserid',
    #'swingers',
    #'south',
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.contenttypes',
    'django.contrib.auth',
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
    'django_comments',
    'django_pdb',
    'django_select2',
    'markup_deprecated',
    'smart_selects',
    'crispy_forms',
    'guardian',
    'debug_toolbar',
    'debug_toolbar_htmltidy',
    'mail_templated',
    'compressor',
    'gunicorn',
    'django_nose',
    'envelope',
    'reversion',
    'tastypie',
    'rest_framework',
    'webtemplate_dpaw',
    'django_wsgiserver',
)

PROJECT_APPS = (
    'pythia',
    'pythia.documents',
    'pythia.projects',
    'pythia.reports',
)

INSTALLED_APPS += THIRD_PARTY_APPS
INSTALLED_APPS += PROJECT_APPS

MIDDLEWARE_CLASSES = (
    #'swingers.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',                                         
    'django.middleware.common.CommonMiddleware',                                                    
    'django.middleware.csrf.CsrfViewMiddleware',                                                    
    'django.contrib.auth.middleware.AuthenticationMiddleware',                                      
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',                               
    'django.contrib.messages.middleware.MessageMiddleware',                                         
    'django.middleware.clickjacking.XFrameOptionsMiddleware',                                       
    'django.middleware.security.SecurityMiddleware',                                                
    'reversion.middleware.RevisionMiddleware',                                                      
    'dpaw_utils.middleware.SSOLoginMiddleware',  

    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_pdb.middleware.PdbMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django_browserid.context_processors.browserid',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.core.context_processors.static',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'pythia.context_processors.persona',
)

ROOT_URLCONF = 'sdis.urls'

TEMPLATES = [                                                                                       
    {                                                                                               
        'BACKEND': 'django.template.backends.django.DjangoTemplates',                               
        'DIRS': [root('templates')],                                                                
        'APP_DIRS': True,                                                                           
        'OPTIONS': {                                                                                
            'context_processors': [                                                                 
                "django.contrib.auth.context_processors.auth",                                      
                "django.core.context_processors.debug",                                             
                "django.core.context_processors.i18n",                                              
                "django.core.context_processors.media",                                             
                "django.core.context_processors.static",                                            
                "django.core.context_processors.tz",                                                
                "django.contrib.messages.context_processors.messages",                              
                "django.core.context_processors.request",                                           
                #"sdis.context_processors.standard",                                               
            ],                                                                                      
        },                                                                                          
    },                                                                                          
] 
#TEMPLATE_LOADERS = (
#    ('django.template.loaders.cached.Loader', (
#       'django.template.loaders.filesystem.Loader',
#        'django.template.loaders.app_directories.Loader',
#    )),)
#TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'pythia/templates'),)


WSGI_APPLICATION = 'sdis.wsgi.application'

# Database
DATABASES = {'default': database.config()}

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
MEDIA_ROOT = root('..', 'media')
MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = root('..', 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)


# User settings - enable SDIS custom user.
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
#   'pythia.backends.PythiaBackend',
)

ANONYMOUS_USER_ID = 100000
AUTH_USER_MODEL = 'pythia.User'
#PERSONA_LOGIN = os.environ.get('PERSONA_LOGIN', False)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = LOGIN_URL
LOGOUT_URL = '/logout/'
LOGOUT_REDIRECT_URL = LOGOUT_URL

# django-tastypie settings                                                                          
TASTYPIE_ALLOW_MISSING_SLASH = True                                                                 
TASTYPIE_DATETIME_FORMATTING = 'iso-8601-strict'                                                    
TASTYPIE_DEFAULT_FORMATS = ['json', 'html']                                                         
API_LIMIT_PER_PAGE = 0 


# LDAP settings
#AUTH_LDAP_SERVER_URI = os.environ.get('LDAP_SERVER_URI', None)
#AUTH_LDAP_BIND_DN = os.environ.get('LDAP_BIND_DN', None)
#AUTH_LDAP_BIND_PASSWORD = os.environ.get('LDAP_BIND_PASSWORD', None)

#AUTH_LDAP_ALWAYS_UPDATE_USER = False
#AUTH_LDAP_AUTHORIZE_ALL_USERS = True
#AUTH_LDAP_FIND_GROUP_PERMS = False
#AUTH_LDAP_MIRROR_GROUPS = False
#AUTH_LDAP_CACHE_GROUPS = False
#AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300

#AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
#    LDAPSearch("DC=corporateict,DC=domain", ldap.SCOPE_SUBTREE,
#               "(sAMAccountName=%(user)s)"),
#    LDAPSearch("DC=corporateict,DC=domain", ldap.SCOPE_SUBTREE,
#               "(mail=%(user)s)"),
#)

#AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
#    "DC=corporateict,DC=domain",
#    ldap.SCOPE_SUBTREE, "(objectClass=group)"
#)

#AUTH_LDAP_GLOBAL_OPTIONS = {
#    ldap.OPT_X_TLS_REQUIRE_CERT: False,
#    ldap.OPT_REFERRALS: False,
#}

#AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")

#AUTH_LDAP_USER_ATTR_MAP = {
#    'first_name': "givenName",
#    'last_name': "sn",
#    'email': "mail",
#}


# Django-Restframework
REST_FRAMEWORK = {
# Use hyperlinked styles by default.
# Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS': 'rest_framework.serializers.HyperlinkedModelSerializer',

# Use Django's standard `django.contrib.auth` permissions,
# or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly']
}

# Misc settings
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'alerts.corporateict.domain')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 25)

# Envelope email
ENVELOPE_EMAIL_RECIPIENTS = ['sdis@DPaW.wa.gov.au']                                               
ENVELOPE_USE_HTML_EMAIL = True

# old email settings
#EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None)
##EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None)
#EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', False)
#DEFAULT_FROM_EMAIL = '"SDIS" <sdis-noreply@dpaw.wa.gov.au>'


COMPRESS_ENABLED = False

SOUTH_TESTS_MIGRATE = False
SKIP_SOUTH_TESTS = True
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'


DEBUG_TOOLBAR_CONFIG = {
    'HIDE_DJANGO_SQL': False,
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': 'sdis.utils.show_toolbar'
}

# Logging configuration
LOG_FOLDER = root('..', 'log') 
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'precise': {                                                                                
            'format': '{%(asctime)s.%(msecs)d}  %(message)s [%(levelname)s %(name)s]',              
            'datefmt': '%H:%M:%S'                                                                   
         }, 
        'default': {                                                                                
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
            'filename': os.path.join(LOG_FOLDER, 'sdis.log'),
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
    #TEMPLATE_LOADERS = (
    #    'django.template.loaders.filesystem.Loader',
    #    'django.template.loaders.app_directories.Loader',
    #)
