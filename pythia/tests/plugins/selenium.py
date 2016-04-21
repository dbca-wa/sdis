from pythia.tests import SeleniumTestCase
from nose.plugins.base import Plugin


class SeleniumSelector(Plugin):
    def options(self, parser, env):
        parser.add_option("--exclude-selenium", default=None, dest="selenium",
                          action="store_false",
                          help="Skip all selenium tests.")
        parser.add_option("--selenium", default=None, dest="selenium",
                          action="store_true",
                          help="Perform all selenium tests (default)")

    def configure(self, options, config):
        self.selenium = options.selenium
        self.enabled = options.selenium is not None

    def wantClass(self, cls):
        if self.selenium:
            return issubclass(cls, SeleniumTestCase)
        elif issubclass(cls, SeleniumTestCase):
            return False
