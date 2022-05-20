##############################################################################
#
# Copyright (c) 2004-2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Logging support.

This code is pretty much untested and was only mechanically refactored.

The module name is not 'logging' because of a name collision with Python's
logging module.
"""
import logging
import logging.config
import os
import os.path
import warnings

import zope.testrunner.feature


class Logging(zope.testrunner.feature.Feature):

    active = True

    def global_setup(self):
        # Get the log.ini file either from the envvar
        # ``ZOPE_TESTRUNNER_LOG_INI`` or file ``log.ini`` in
        # the current working directory.
        logini = os.environ.get("ZOPE_TESTRUNNER_LOG_INI")
        if logini is not None and not os.path.exists(logini):
            warnings.warn(
                "ERROR: file specified by envvar ZOPE_TESTRUNNER_LOG_INI` "
                "does not exist")
            logini = None
        if logini is None:
            logini = "log.ini"
        logini = os.path.abspath(logini)  # make absolute
        if os.path.exists(logini):
            logging.config.fileConfig(logini, disable_existing_loggers=False)
            # remember the log configuration in envvar for use
            # by child processes
            os.environ["ZOPE_TESTRUNNER_LOG_INI"] = logini
        else:
            # If there's no log.ini, cause the logging package to be
            # silent during testing.
            root = logging.getLogger()
            root.addHandler(NullHandler())
            logging.basicConfig()

        if "LOGGING" in os.environ:
            level = int(os.environ["LOGGING"])
            logging.getLogger().setLevel(level)


class NullHandler(logging.Handler):
    """Logging handler that drops everything on the floor.

    We require silence in the test environment.  Hush.
    """

    def emit(self, record):
        pass
