# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 Zope Corporation and Contributors.
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
"""Test runner based on zope.testing.testrunner
"""
from collective.xmltestreport.formatter import XMLOutputFormattingWrapper
from zope.testrunner.runner import Runner

import os
import sys


# Test runner and execution methods


class XMLAwareRunner(Runner):
    """Add output formatter delegate to the test runner before execution
    """

    def configure(self):
        super(XMLAwareRunner, self).configure()
        self.options.output = XMLOutputFormattingWrapper(
            self.options.output, cwd=os.getcwd())


def run(defaults=None, args=None, script_parts=None):
    """Main runner function which can be and is being used from main programs.

    Will execute the tests and exit the process according to the test result.

    """
    failed = run_internal(defaults, args, script_parts=script_parts)
    sys.exit(int(failed))


def run_internal(defaults=None, args=None, script_parts=None):
    """Execute tests.

    Returns whether errors or failures occured during testing.

    """

    runner = XMLAwareRunner(defaults, args, script_parts=script_parts)
    try:
        runner.run()
    finally:
        # Write XML file of results if -x option is given
        if runner.options and runner.options.xmlOutput:
            runner.options.output.writeXMLReports()

    return runner.failed
