##############################################################################
#
# Copyright (c) 2020 Zope Foundation and Contributors.
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
"""A large number of sample tests."""

import unittest


class Layer1:
    """A layer that can't be torn down."""

    @classmethod
    def setUp(self):
        pass

    @classmethod
    def tearDown(self):
        raise NotImplementedError


class Layer2:

    @classmethod
    def setUp(self):
        pass

    @classmethod
    def tearDown(self):
        pass


class TestNoTeardown(unittest.TestCase):

    layer = Layer1

    def test_something(self):
        pass


def make_TestMany():
    attrs = {'layer': Layer2}
    # Add enough failing test methods to make the concatenation of all their
    # test IDs (formatted as "test_foo (sampletests_many.TestMany)")
    # overflow the capacity of a pipe.  This is system-dependent, but on
    # Linux since 2.6.11 it defaults to 65536 bytes, so will overflow by the
    # time we've written 874 of these test IDs.  If the pipe capacity is
    # much larger than that, then this test might be ineffective.
    for i in range(1000):
        attrs['test_some_very_long_test_name_with_padding_%03d' % i] = (
            lambda self: self.fail())
    return type('TestMany', (unittest.TestCase,), attrs)


TestMany = make_TestMany()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNoTeardown))
    suite.addTest(unittest.makeSuite(TestMany))
    return suite


if __name__ == '__main__':
    unittest.main()
