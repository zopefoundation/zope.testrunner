##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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

"""Sample tests that produce output on stdout and stderr."""

import sys
import unittest


class Test(unittest.TestCase):

    def test_stdout_success(self):
        sys.stdout.write("stdout output on success\n")

    def test_stdout_failure(self):
        sys.stdout.write("stdout output on failure\n")
        self.assertTrue(False)

    def test_stdout_error(self):
        sys.stdout.write("stdout output on error\n")
        raise Exception("boom")

    def test_stderr_success(self):
        sys.stderr.write("stderr output on success\n")

    def test_stderr_failure(self):
        sys.stderr.write("stderr output on failure\n")
        self.assertTrue(False)

    def test_stderr_error(self):
        sys.stderr.write("stderr output on error\n")
        raise Exception("boom")


def test_suite():
    return unittest.makeSuite(Test)
