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

import time
import unittest


class ClassicLeakable:
    def __init__(self):
        self.x = 'x'


class Leakable:
    def __init__(self):
        self.x = 'x'


leaked = []


class TestSomething(unittest.TestCase):

    def testleak(self):
        leaked.append((ClassicLeakable(), Leakable(), time.time()))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestSomething))
    return suite


if __name__ == '__main__':
    unittest.main()
