##############################################################################
#
# Copyright (c) 2023 Zope Foundation and Contributors.
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
"""Unit tests for the XML reports
"""
import contextlib
import io
import os
import os.path
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from zope import testrunner


class Base(unittest.TestCase):

    def tearDown(self):
        self._cleanup(self.reports_folder)
        return super().tearDown()

    def _cleanup(self, path):
        if path.exists():
            [x.unlink() for x in path.iterdir()]
            path.rmdir()


class TestXMLOutput(Base):
    """Test the XML output of `zope.testrunner`

    By default, `zope.testrunner` reports the results to the terminal.
    CI systems however, need a machine readable format
    to actually parse the results and display them.

    The `JUnit` package from the Java community, long ago,
    created an XML report format that since then
    every CI system is able to read.

    The `--xml` option tells the test runner to produce such a report.
    """

    def setUp(self):
        this_directory = os.path.split(__file__)[0]
        directory_with_tests = Path(this_directory, 'testrunner-ex')
        self.arg_defaults = [
            '--path', str(directory_with_tests),
            '--tests-pattern', '^sampletestsf?$',
        ]
        self.default_argv = 'test -u --xml=. -t sample3'.split()
        self.reports_folder = Path('testreports')
        self._cleanup(self.reports_folder)

    def _run_tests(self):
        stream1 = io.StringIO()
        stream2 = io.StringIO()
        with contextlib.redirect_stdout(stream1):
            with contextlib.redirect_stderr(stream2):
                testrunner.run_internal(self.arg_defaults, self.default_argv)

    def test_xml_report(self):
        self._run_tests()
        # A report has been created:
        self.assertTrue(self.reports_folder.exists())

        # There are 5 reports:
        reports = [x for x in self.reports_folder.iterdir()]
        self.assertEqual(len(reports), 5)

    def test_xml_report_details(self):
        """Let's look at an individual report."""
        self._run_tests()
        report = self.reports_folder / 'sample3.sampletests.TestA.xml'

        # 3 tests were run with no errors nor failures:
        content = report.read_text()
        self.assertIn(' tests="3" ', content)
        self.assertIn(' errors="0" ', content)
        self.assertIn(' failures="0" ', content)

        # The specific tests that were run:
        self.assertIn(
            '<testcase classname="sample3.sampletests.TestA" name="test_x1"',
            content)
        self.assertIn(
            '<testcase classname="sample3.sampletests.TestA" name="test_y0"',
            content)
        self.assertIn(
            '<testcase classname="sample3.sampletests.TestA" name="test_z0"',
            content)


class TextXMLOutputWithErrors(Base):
    """If errors/failures happen, they are also reported in the XML files

    Code copied and adapted from `testrunner-errors.rst`
    """

    def setUp(self):
        this_directory = os.path.split(__file__)[0]
        tmpdir = tempfile.mkdtemp()
        directory_with_tests = os.path.join(tmpdir, 'testrunner-ex')
        self.reports_folder = Path('testreports')

        source = os.path.join(this_directory, 'testrunner-ex')
        n = len(source) + 1
        for root, dirs, files in os.walk(source):
            dirs[:] = [d for d in dirs if d != ".svn"]  # prune cruft
            os.mkdir(os.path.join(directory_with_tests, root[n:]))
            for f in files:
                shutil.copy(os.path.join(root, f),
                            os.path.join(directory_with_tests, root[n:], f))

        self.defaults = [
            '--path', directory_with_tests,
            '--tests-pattern', '^sampletestsf?$',
            '--xml=.',
            ]
        self._cleanup(self.reports_folder)

    def _run_tests(self):
        stream1 = io.StringIO()
        stream2 = io.StringIO()
        with contextlib.redirect_stdout(stream1):
            with contextlib.redirect_stderr(stream2):
                testrunner.run_internal(self.defaults)

    def test_xml_report_with_errors(self):
        sys.argv = 'test --tests-pattern ^sampletests(f|_e|_f)?$ '.split()
        self._run_tests()

        self.assertTrue(self.reports_folder.exists())
        self.assertEqual(len([x for x in self.reports_folder.iterdir()]), 106)

    def test_xml_report_with_errors_details(self):
        sys.argv = 'test --tests-pattern ^sampletests(f|_e|_f)?$ '.split()
        self._run_tests()
        report = self.reports_folder / 'sample2.sampletests_e.Test.xml'
        self.assertTrue(report.exists())

        content = report.read_text()
        self.assertIn(' tests="5" ', content)
        self.assertIn(' errors="1" ', content)
        self.assertIn(' failures="0" ', content)

        # The error message is reported:
        self.assertIn('<error message="name \'y\' is not defined"', content)

        # And the traceback is there as well:
        self.assertIn('sampletests_e.py", line 47, in test3', content)

    def test_xml_report_with_failures(self):
        sys.argv = 'test --tests-pattern ^sampletests(f|_e|_f)?$ '.split()
        self._run_tests()
        report = (
            self.reports_folder /
            'doctest-src-zope-testrunner-tests-testrunner-ex-sample2-e.rst.xml'
        )
        self.assertTrue(report.exists())

        content = report.read_text()
        self.assertIn(' tests="1" ', content)
        self.assertIn(' errors="0" ', content)
        self.assertIn(' failures="1" ', content)

        # The failure is reported:
        self.assertIn('Exception raised:', content)
