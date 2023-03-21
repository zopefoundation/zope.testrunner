##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
"""Unit tests for the testrunner's subunit integration."""


import io
import sys
import unittest

from zope.testrunner import formatter


try:
    import subunit
    subunit
except ImportError:
    def test_suite():
        return unittest.TestSuite()
else:

    class TestSubunitTracebackPrintingMixin:

        def makeByteStringFailure(self, text, encoding):
            try:
                # It's more accurate to just use the text directly.
                self.fail(text)
            except self.failureException:
                return sys.exc_info()

        def test_print_failure_containing_utf8_bytestrings(self):
            exc_info = self.makeByteStringFailure(chr(6514), 'utf8')
            self.subunit_formatter.test_failure(self, 0, exc_info)
            assert b"AssertionError: \xe1\xa5\xb2" in self.output.getvalue()
            # '\xe1\xa5\xb2'.decode('utf-8') == chr(6514)

        def test_print_error_containing_utf8_bytestrings(self):
            exc_info = self.makeByteStringFailure(chr(6514), 'utf8')
            self.subunit_formatter.test_error(self, 0, exc_info)
            assert b"AssertionError: \xe1\xa5\xb2" in self.output.getvalue()
            # '\xe1\xa5\xb2'.decode('utf-8') == chr(6514)

    class TestSubunitTracebackPrinting(
            TestSubunitTracebackPrintingMixin, unittest.TestCase):

        def setUp(self):
            class FormatterOptions:
                verbose = False
            options = FormatterOptions()

            self.output = io.BytesIO()
            self.subunit_formatter = formatter.SubunitOutputFormatter(
                options, stream=self.output)

    class TestSubunitV2TracebackPrinting(
            TestSubunitTracebackPrintingMixin, unittest.TestCase):

        def setUp(self):
            class FormatterOptions:
                verbose = False
            options = FormatterOptions()

            self.output = io.BytesIO()
            self.subunit_formatter = formatter.SubunitV2OutputFormatter(
                options, stream=self.output)

    def test_suite():
        return unittest.defaultTestLoader.loadTestsFromName(__name__)
