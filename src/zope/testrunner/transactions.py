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
"""Transaction collection support.
"""

import sys

import zope.testrunner.feature

class Transaction(zope.testrunner.feature.Feature):

    active = True

    def before_test(self, test):
        try:
            import transaction
        except ImportError:
            self.had_resources = True
            return
        txn = transaction.get()
        self.had_resources = bool(txn._resources)
        if self.had_resources:
            self.runner.options.output.info("Test %s received an unclean transaction:"
                                             "\n  %r" % (test, txn._resources, ))

    def after_test(self, test):
        if self.had_resources:
            return
        import transaction
        txn = transaction.get()
        if txn._resources:
            self.runner.options.output.error("Test %s left an unclean transaction:"
                                             "\n  %r" % (test, txn._resources, ))
            txn.abort()


