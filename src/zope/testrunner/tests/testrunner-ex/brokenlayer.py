##############################################################################
#
# Copyright (c) 2012-2018 Zope Foundation and Contributors.
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
"""Sample tests with layers that have broken set up and tear down."""

import unittest


class BrokenSetUpLayer:

    @classmethod
    def setUp(cls):
        raise ValueError('No value is good enough for me!')

    @classmethod
    def tearDown(cls):
        pass


class BrokenTearDownLayer:

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        raise TypeError('You are not my type.  No-one is my type!')


class TestSomething1(unittest.TestCase):

    layer = BrokenSetUpLayer

    def test_something(self):
        pass


class TestSomething2(unittest.TestCase):

    layer = BrokenTearDownLayer

    def test_something(self):
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSomething1))
    suite.addTest(unittest.makeSuite(TestSomething2))
    return suite
