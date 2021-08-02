"""SDIS Test settings.

Patch geos:
https://stackoverflow.com/questions/18643998/geodjango-geosexception-error
"""

from .settings import *

# Additional apps required for testing.
INSTALLED_APPS += ('django_nose',)
POSTGIS_VERSION = (3, 1, 2)

SOUTH_TESTS_MIGRATE = False
SKIP_SOUTH_TESTS = True

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--nocapture',
    '--nologcapture',
    '--with-fixture-bundling',
    # '--with-coverage',
    '--cover-package=pythia',
    '--verbosity=3',
    '--detailed-errors']

CACHES = {"default": {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', }}  # noqa
