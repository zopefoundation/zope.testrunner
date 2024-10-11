##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
import doctest
import unittest


class TestSomething(unittest.TestCase):

    def test_set_trace1(self):
        x = 1
        import pdb  # noqa: T100 import for pdb found
        pdb.set_trace()  # noqa: T100 pdb.set_trace found
        y = x  # noqa: F841

    def test_set_trace2(self):
        f()

    def test_post_mortem1(self):
        x = 1  # noqa: F841
        raise ValueError

    def test_post_mortem2(self):
        g()

    def test_post_mortem_failure1(self):
        x = 1
        y = 2
        assert x == y

    @unittest.skip("skipped test")
    def test_skipped(self):
        self.fail('test should have been skipped')


def f():
    x = 1
    import pdb  # noqa: T100 import for pdb found
    pdb.set_trace()  # noqa: T100 pdb.set_trace found
    y = x  # noqa: F841


def g():
    x = 1  # noqa: F841
    raise ValueError


def set_trace3(self):
    """
    >>> x = 1
    >>> if 1:
    ...     import pdb; pdb.set_trace()
    ...     y = x
    """


def set_trace4(self):
    """
    >>> f()
    """


def post_mortem3(self):
    """
    >>> x = 1
    >>> raise ValueError
    """


def post_mortem4(self):
    """
    >>> g()
    """


def post_mortem_failure2():
    """
    >>> x = 1
    >>> x
    2
    """


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestSomething),
        doctest.DocFileSuite('set_trace5.rst'),
        doctest.DocFileSuite('set_trace6.rst'),
        doctest.DocFileSuite('post_mortem5.rst'),
        doctest.DocFileSuite('post_mortem6.rst'),
        doctest.DocFileSuite('post_mortem_failure.rst'),
    ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
