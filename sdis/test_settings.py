from .settings import *

# Additional apps required for testing.
INSTALLED_APPS += (
    'django_nose',
)

SOUTH_TESTS_MIGRATE = False
SKIP_SOUTH_TESTS = True
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Test runner settings.
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--nocapture',
    '--nologcapture',
    '--with-fixture-bundling',
    #'--with-coverage',
    '--cover-package=pythia',
    '--verbosity=2',
    '--detailed-errors']
