from logging import DEBUG
from logging import getLogger
from os import chdir
from os import environ
from os import getcwd
from os.path import dirname
from os.path import join
from unittest import TestCase
from warnings import catch_warnings

from ..logsupport import Logging


setup_logging = Logging.global_setup
setup_logging = getattr(setup_logging, "__func__", setup_logging)
evn = "ZOPE_TESTRUNNER_LOG_INI"


class LogsupportTests(TestCase):
    def setUp(self):
        # save root logger config
        logger = getLogger()
        self.logconfig = lc = logger.__dict__.copy()
        for n in ("filters", "handlers"):
            lc[n] = lc[n][:]  # copy
            del getattr(logger, n)[:]  # clear
        # save working directory
        self.cwd = getcwd()
        # save and clear envvar
        self.envvar = ev = environ.get(evn, self)
        if ev is not self:
            del environ[evn]

    def tearDown(self):
        # restore working directory
        chdir(self.cwd)
        # restore root logger configuration
        logger = getLogger()
        logger.__dict__.update(self.logconfig)
        # restore envvar
        ev = self.envvar
        if ev is not self:
            environ[evn] = ev
        elif evn in environ:
            del environ[evn]

    def test_via_cwd(self):
        chdir(join(dirname(__file__), "logsupport"))
        self.check_logging()

    def test_via_envvar(self):
        lc = join(dirname(__file__), "logsupport", "log.ini")
        environ[evn] = lc
        self.check_logging()

    def test_via_bad_envvar(self):
        chdir(join(dirname(__file__), "logsupport"))
        environ[evn] = "not_existing"
        with catch_warnings(record=True) as w:
            self.check_logging()
            self.assertEqual(len(w), 1)

    def check_logging(self):
        setup_logging(None)
        logger = getLogger()
        self.assertEqual(logger.level, DEBUG)
        self.assertEqual(len(logger.handlers), 1)
        lc = join(dirname(__file__), "logsupport", "log.ini")
        self.assertEqual(environ[evn], lc)
