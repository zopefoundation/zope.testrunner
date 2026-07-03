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
"""Doc test support for the test runner.
"""

import doctest
import io
import sys
import unittest

import zope.testrunner.feature
from zope.testrunner.exceptions import DocTestFailureException


class DocTest(zope.testrunner.feature.Feature):

    active = True

    def global_setup(self):
        options = self.runner.options
        output = options.output

        self.old_reporting_flags = doctest.set_unittest_reportflags(0)

        reporting_flags = 0
        if options.ndiff:
            reporting_flags = doctest.REPORT_NDIFF
        if options.udiff:
            if reporting_flags:
                output.error(
                    "Can only give one of --ndiff, --udiff, or --cdiff")
                sys.exit(1)
            reporting_flags = doctest.REPORT_UDIFF
        if options.cdiff:
            if reporting_flags:
                output.error(
                    "Can only give one of --ndiff, --udiff, or --cdiff")
                sys.exit(1)
            reporting_flags = doctest.REPORT_CDIFF
        if options.report_only_first_failure:
            reporting_flags |= doctest.REPORT_ONLY_FIRST_FAILURE

        if reporting_flags:
            doctest.set_unittest_reportflags(reporting_flags)

    def global_shutdown(self):
        doctest.set_unittest_reportflags(self.old_reporting_flags)


# Use a special exception for the test runner.
doctest.DocTestCase.failureException = DocTestFailureException


if sys.version_info >= (3, 15):
    # Python 3.15 changed ``doctest.DocTestCase.runTest`` to report each
    # example as a separate subtest of the enclosing unittest result
    # (python/cpython#108885).  These reports happen while the doctest
    # machinery has ``sys.stdout`` redirected to its internal buffer, so
    # zope.testrunner's immediate failure output would be swallowed by that
    # buffer and corrupt the output of the following examples.  Restore the
    # pre-3.15 behavior of raising a single failure for the whole doctest
    # after ``sys.stdout`` has been restored.
    def _runTest(self):
        test = self._dt_test
        optionflags = self._dt_optionflags

        if not (optionflags & doctest.REPORTING_FLAGS):
            # The option flags don't include any reporting flags,
            # so add the default reporting flags
            optionflags |= doctest._unittest_reportflags

        runner = doctest.DocTestRunner(optionflags=optionflags,
                                       checker=self._dt_checker,
                                       verbose=False)
        out = io.StringIO()
        runner.DIVIDER = "-" * 70
        results = runner.run(test, out=out.write, clear_globs=False)
        if results.skipped == results.attempted:
            raise unittest.SkipTest("all examples were skipped")

        if results.failed:
            raise self.failureException(
                self.format_failure(out.getvalue().rstrip('\n')))

    doctest.DocTestCase.runTest = _runTest
